import numpy as np
# from files import loadConfig,saveConfig
import math,copy
from enum import Enum, auto
import csv,pandas
import functools
global_max_rounds=999
global_max_rounds_test=5
global_armorconst=0.06
INF=float('inf')
global_observer_list=[]
flag_showinfo_attack=True
flag_showinfo_regen=True
flag_input_in_battle=True
flag_debuglog=3
global_levelname=["_","下级佣兵","中级佣兵","高级佣兵","特级佣兵","王牌佣兵", #5
    "荣耀佣兵","辉煌佣兵","准职业者","黑铁职业者","青铜职业者",#10
    "白银职业者","黄金职业者","蓝玉职业者","紫晶职业者","半步英雄",
    "英雄一阶","英雄二阶","英雄三阶","英雄四阶","英雄五阶"]#15
global_Level = Enum('Level', tuple(global_levelname[1:]))

def To_List(obj) -> list:
    """将对象转换为列表，如果已经是列表则返回原列表"""
    if isinstance(obj,list):
        return obj
    else:
        return [obj]
def DefaultValue_If_None(x=None,value=None):
    """如果x为None，则返回value，否则返回x"""
    if x is None:
        x=value
    return x
def getnew(input,key="new"):
    """获取字典或对象的属性，如果不存在则返回None"""
    if input is not None:
        try: input=input[key]
        except:pass
    return input
def print_objectswith_str_(*objlist_list,end=" "):
    """打印对象列表，如果不是可迭代对象则直接打印"""
    for objlist in objlist_list:
        if isinstance(objlist,str) or not hasattr(objlist,"__iter__"):
            print(objlist,end=end)
        else:
            for obj in objlist:
                print_objectswith_str_(obj,end=end)
                print()
def keep2dim(K):

    if K is None:
        K=[]
    if not hasattr(K,"__len__"):
        K=[K]
    if not hasattr(K[0],"__len__"):
        K=[K]
    return K
def dict_pick(dic,keyslist):
    """从字典中选择指定的键，返回一个新的字典"""
    newdic={}
    for key in keyslist:
        if key in dic.keys():
            newdic[key]=dic[key]
    return newdic

        
def ar2array(inputs):
    return np.array(inputs,dtype=float).flatten()
def getvalue(var,key="value"):
    """获取对象或字典的指定属性或键的值"""
    if hasattr(var,key):
        return getattr(var,key)
    else: return var

    ##--------
def get_global_from(name_or_baseid,copyflag=False,from_list=None):
    if from_list is None:
        from_list = global_MonsterBaseList + global_SkillList + global_EffectList
    for obj in from_list:
        if obj.name == name_or_baseid or obj.baseID == name_or_baseid:
            return copy.deepcopy(obj) if copyflag else obj
    return None
def get_global_skill(name_or_baseid,copyflag=False):
    return get_global_from(name_or_baseid,copyflag=copyflag,from_list=global_SkillList)
def get_global_effect(name_or_baseid,copyflag=False):
    return get_global_from(name_or_baseid,copyflag=copyflag,from_list=global_EffectList)
def get_global_actor(name_or_baseid,copyflag=False):
    return get_global_from(name_or_baseid,copyflag=copyflag,from_list=global_MonsterBaseList)
class SkillType(Enum):
    """技能类型枚举"""
    Active =auto()# 1
    Passive =auto()# 2
    Summon =auto()# 3
    Support =auto()# 4
    Aura =auto()# 5
    Strategy =auto()
class DeliveryType(Enum):#这个是关键！施加魔法效果
    """技能施法方式枚举"""
    Self =auto()# 1
    Area =auto()# 2
    Contact=auto()
    Target =auto()# 3
    # Targets =auto()   
#OnEffectStart( caster,target,*args)
#OnEffectEnd(caster,target,*args)
class TargetPermit(Enum):
    """技能目标许可枚举"""
    Self =auto()# 1
    Ally =auto()# 2
    Enemy =auto()# 3

class EffectType(Enum):# archetype仅仅简化，实际上从根本上允许脚本写法
    """魔法效果类型枚举"""
    Empty=0
    ValueModifier =auto()# 1
    PeakValueModifier =auto()# 1 
    MagicImmunity =auto() 
    Mute =auto()#  
    Disarm =auto()#  
    Break =auto()#  #禁用被动
    Stun =auto()#  
    Summon =auto()#  
    Image =auto()
    ManaBurn =auto()
    Ethereal =auto()
    Absorb=auto()



class StrategyEffectType(Enum):
    """策略效果类型枚举"""
    Aura= auto()
    Support = auto()

class ActorValueType(Enum):
    """Actor属性枚举"""
    level=0

    health = auto()
    mana = auto()
    
    attack=auto()# 攻击
    defence=auto()# 防御
    armor=auto()# 护甲表示对物理类伤害的削弱能力，每点护甲会意味着在受到物理伤害时每一点生命将额外多承受6%的伤害
    atkrate=auto() # 攻速 表示攻击速度，战斗者每回合普攻造成的伤害会乘上一个攻速带来的系数，具体为[攻速的平方根/10]
    avoid=auto() #闪避率（单位1%,log映射）
    block=auto()# 伤害格挡 高级的物理减伤方式，在物理伤害进行过护甲减伤的基础上进一步减少伤害
    magicresist=auto()
    magicblock=auto()
    healthregen=auto() # 生命回复 每回合开始的时候自身会恢复和数值相同的生命，若为负则相当于生命移除
    manaregen=auto() # 魔法回复 每回合开始的时候自身会恢复和数值相同的魔法
    magicpower=auto() # 法术能量 能够增强技能的效果，部分效果(主要是伤害)会加上[法术能量*括号中的系数]的数值，
    STRE=auto()
    AGIL=auto()
    INTEL=auto()
    custom=auto()
    amount=auto()# 物品数量，装备类物品的数量，或是技能的施法次数等
AVhasMaxList=[ActorValueType.health,ActorValueType.mana,ActorValueType.amount]#有最大值的属性列表
class DamageType(Enum):
    """伤害类型枚举"""
    Physical =auto()# 1
    Poison =auto()# 2
    Magic =auto()# 3
    Pure =auto()# 4
    LifeRemove =auto()# 5
def EnumConvert(enumclass, value):
    """将值转换为枚举类型"""
    #None to None
    #nan to None
    #float or int to enum()
    #str to enum[]
    if isinstance(value, enumclass):
        return value
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:#"2" to 2
        float(value)
        value=int(value)
    except:
        pass
    
    if isinstance(value, (int, float)):
        return enumclass(value)
    if isinstance(value, str):
        return enumclass[value]
class ActorValue():
    """Actor属性类，表示一个角色的属性值"""
    aliases = {
        'value': 'currentvalue',
        'current': 'currentvalue',
        'max': 'maxvalue',
        'base': 'basevalue',
    }
    def __init__(self,type_=ActorValueType.health,currentvalue=0,maxvalue=None,basevalue=None) -> None:
        avtype=ActorValueType(type_)
        self.AV_Type=avtype
        self.ResetValue(currentvalue=currentvalue,maxvalue=maxvalue,basevalue=basevalue)
        # self.

    def __str__(self) -> str:
        return "value=%s, max=%s"%(self.currentvalue,self.maxvalue)
    def ResetValue(self,currentvalue=0,maxvalue=None,basevalue=None):
        if isinstance(currentvalue,list):
            self.currentvalue=currentvalue[0]
            self.maxvalue=currentvalue[1]
            self.basevalue=currentvalue[2] if len(currentvalue>2) else self.maxvalue
            
            return
        elif isinstance(currentvalue,ActorValue):
            print("currentvalue=",currentvalue)
            self.currentvalue=currentvalue.currentvalue
            self.maxvalue=currentvalue.maxvalue
            self.basevalue=currentvalue.basevalue
            return
        else:
            self.currentvalue=currentvalue
            self.maxvalue=DefaultValue_If_None(maxvalue,currentvalue)
            self.basevalue=DefaultValue_If_None(basevalue,self.maxvalue)
    def __setattr__(self, name, value):
        name = self.aliases.get(name, name)
        object.__setattr__(self, name, value)
    def __getattr__(self, name):
        if name == "aliases":
            raise AttributeError  # http://nedbatchelder.com/blog/201010/surprising_getattr_recursion.html
        name = self.aliases.get(name, name)
        return object.__getattribute__(self, name)
    def ModValue(self,value,maxbound=None,zerobound=False ):    
        value_final=self.currentvalue+value
        # print(value_final,self.maxvalue)
        maxbound=DefaultValue_If_None(maxbound,True if self.AV_Type in AVhasMaxList else False)
        value_final=_clip(value_final,max_=self.maxvalue if maxbound else None,min_=0 if zerobound else None)

        self.currentvalue=value_final
        return value_final-value #实际变化
    def ModPeakValue(self,value,flag_proportion=True,flag_clipup=True ):
        oldmax=self.maxvalue
        self.maxvalue+= value
        if flag_clipup and self.maxvalue<self.currentvalue:
            self.currentvalue=self.maxvalue#截断
        if flag_proportion and self.maxvalue>self.currentvalue and oldmax>0:
            self.currentvalue*=(self.maxvalue/oldmax)#按比例缩放
    def get_percentage(self):
        return self.currentvalue/self.maxvalue

def norm01(value):
    """将值限制在0到1之间"""
    return min(max(0.0,value),1.0)
def strcat(*kargs,space=True):
    st=""
    for x in kargs:
        st+=str(x)+ (" " if space else  "")
    return st

# def criticalmult(criticalAtk,trigger=False,average=True):
#     """计算暴击倍率"""
#     if trigger:
#         return criticalAtk[0]
#     else:
#         return 1+(criticalAtk[0]-1)*criticalAtk[1]/100 if average else 1
class Skill():
    """技能类，表示一个角色的技能"""
    def __init__(self,name="",baseID=0,default_param="",parameters=[],description="" 
            ,skilltype=None,delivery=None,targetpermit=None,mana_cost=0,ammunition=1,effect_dict=None  ): 

        
        self.name=name
        self.baseID=baseID
        self.default_param=default_param
        self.description=description
        # self.skilltype=skilltype        #
        self.parameters=parameters
        if effect_dict is None or  isinstance(effect_dict,float) and math.isnan(effect_dict):
            effect_dict={}
        if isinstance(effect_dict,str):
            effect_dict=eval(effect_dict)
        self.effect_list=[]
        
        self.effect_dict=effect_dict #{'寒霜攻击':[1]}

        self.mana_cost=mana_cost

        #以下属性只对active有效
        self.casting_pretime=1#0 瞬发 1 普通 2蓄力
        self.casting_duration=1#0 瞬发 1 普通 2连续生效
        self.casting_cooldown=0 #冷却时间
        self.ammunition=ActorValue(ActorValueType.amount,ammunition)#弹药量
        self.allow_attack=True#该回合正常普通攻击
        self.AI_module=None 


        skilltype=EnumConvert(SkillType, skilltype)        
        self.skilltype=DefaultValue_If_None(skilltype,SkillType.Passive ) 
        delivery=EnumConvert(DeliveryType, delivery)
        self.delivery=DefaultValue_If_None(delivery,DeliveryType.Target if self.skilltype==SkillType.Active else DeliveryType.Contact) 
        targetpermit= [ EnumConvert( TargetPermit, term) for term in To_List( str2list(targetpermit) ) ] if targetpermit is not None else None
        self.targetpermit=To_List( DefaultValue_If_None(targetpermit,[TargetPermit.Enemy ])  )   
    #默认print 返回name字符串
    def __str__(self):
        return "技能:"+str(self.name)

    def showinfo(self):
        """显示技能信息"""
        print("技能名称:",self.name)
        print("技能类型:",self.skilltype)
        print("施法方式:",self.delivery)
        print("目标许可:",[term.name for term in self.targetpermit])
        print("描述:",self.description)
        print("参数:",self.parameters)
        print("法力消耗:",self.mana_cost)
        print("效果列表:")
        for effect in self.effect_list:
            print(" - ",effect.name)
    def process_skill_effects(self,flag_clear=True):
        if flag_clear:
            self.effect_list=[]
        skillbase=self

        for key,paramlist in self.effect_dict.items():
            effect=get_global_effect(key,copyflag=True)
            if len(paramlist)>0:
                ii=paramlist[0]-1
                if ii>=0 and ii<len(skillbase.parameters):
                    effect.magnitude=float(skillbase.parameters[ii])
                else:print("warning: effect param index out of range",skillbase.name,key,paramlist,skillbase.parameters)
            if len(paramlist)>1:
                ii=paramlist[1]-1
                if ii>=0 and ii<len(skillbase.parameters):
                    effect.duration=float(skillbase.parameters[ii])
                else:print("warning: effect param index out of range",skillbase.name,key,paramlist,skillbase.parameters)
            skillbase.effect_list.append(effect)
            #寒霜攻击,a:1,攻击中带有冰寒的力量，将对手缓慢冻结\n第一次命中开始对手攻速降低\v%
            # if skillbase.name=="寒霜攻击":
            #     #寒霜攻击
            #     effect=get_global_effect("寒霜攻击",copyflag=True)

            #     effect.magnitude= -float(skillbase.parameters[0]) if skillbase.parameters else -10
            #     # effect.duration=10  #     默认持续10回合
            #     skillbase.effect_list.append(effect)
            # # 腐蚀毒素,a:3,攻击时释放出毒素缓慢腐蚀敌人的身躯\n每回合攻击额外造成\v点无视防御的物理伤害
            # if skillbase.name=="腐蚀毒素":
            #     #腐蚀毒素
            #     effect=get_global_effect("腐蚀毒素",copyflag=True)
            #     effect.magnitude= -float(skillbase.parameters[0]) if skillbase.parameters else -10
            #     skillbase.effect_list.append(effect)
            if skillbase.name=="闪避":
                # self.skilltype=SkillType.Passive
                # self.delivery=DeliveryType.Self
                #闪避
                # effect=get_global_effect("闪避",copyflag=True)
                # effect.magnitude= float(skillbase.parameters[0]) if skillbase.parameters else 10
                # effect.magnitude= avoid_convert(effect.magnitude,reverse=False)
                effect.dispell_onstatechange=True
                effect.dispell_after_battle=False 
                # skillbase.effect_list.append(effect)
        return skillbase.effect_list

#[自身攻击-目标防御]*我方攻速系数*目标护甲减伤*目标闪避减伤*暴击
def _clip(v,min_=None,max_=None):
    """将值限制在指定范围内"""
    if max_ is not None:
        v=min(v,max_)
    if min_ is not None:    
        v=max(v,min_)
    return v
def AD(a,d):#自身攻击-目标防御
    """计算攻击减防"""
    return max(0,getvalue(a)-getvalue(d))
def factor_attackrate(rate):#攻速系数
    """计算攻速系数"""
    rate=getvalue(rate)
    if rate<=0 : return 0
    return (rate /100)**0.5
def factor_armor(armor):#护甲减伤
    """计算护甲减伤"""
    armor=getvalue(armor)
    if armor>=0:
        return 1/(1+global_armorconst*armor)
    else:
        return (1+global_armorconst*abs(armor))
def factor_avoid(avoid,converted=True):#闪避
    """计算闪避减伤"""
    #命中率叠加因子：log(1-闪避率/100)
    avoid=getvalue(avoid)
    # return  _clip(1-avoid/100  , min_=0,max_=1)
    return  _clip(np.exp( avoid/-100)  , min_=0,max_=1) if converted else  _clip(1-avoid/100  , min_=0,max_=1)
def avoid_convert(avoid,reverse=True):
    if reverse:
        # return (1 - np.exp(avoid)) * 100
        return (1 - np.exp(avoid/-100)) * 100
    else:
        return -100*np.log(1-avoid/100)
def factor_magicresist(resist):#闪避
    """计算魔法抗性减伤"""
    resist=getvalue(resist)
    return  _clip(1-resist/100  , min_=0,max_=1)
def factor_critical(criticalAtk,is_r1,force_trigger=False): #暴击
    """计算暴击系数"""
    ratio,chance,r1_trigger=criticalAtk
    chance=_clip(chance,min_=0)
    flag_certainty=force_trigger>0 or (is_r1 and r1_trigger) or chance>100
    if flag_certainty: return ratio #必然触发
    elif force_trigger<-0.5 :return 0 #不触发
    else: return (1+(ratio-1)*chance/100) #按照百分比期望
 
class Damage():
    def __init__(self,value=0,damagetype=DamageType.Physical): #0=物理， 1=毒素， 2=魔法， 3=纯粹， 4=生命移除
        self.value=value
        self.damagetype=damagetype
class Group():
    """战斗阵营类，表示一组角色"""
    def __init__(self,*args): 
        self.round=0
        self.members=[]

        for term in args:
            if isinstance(term,list):
                self.members.extend(term)
            else :
                self.members.append(term)
            self.members[-1].parent_group=self
        # self.members_alive=self.members                
    def Is_Alive(self):
        is_alive=False
        for term in self.members:
            if term.Is_Alive():
                is_alive=True
        return is_alive
    def Frontier(self):
        """返回阵营中第一个存活的成员的索引"""
        frontier=-1
        for i in range(len(self.members)) :
            term=self.members[i]
            if term.Is_Alive():
                frontier=i
        return frontier      
    def Members_Alive(self):
        """返回阵营中所有存活的成员"""
        return [term for term in self.members if term.Is_Alive()]

    def Show_Members(self,flag_showstate=False):
        """返回阵营中所有成员的名称列表"""
        for i in range(len(self.members)) :
            term=self.members[i]
            if term.Is_Alive():
                frontier=i
        returninfo="["+",".join([term.name for term in self.members]    )   +"]"

        if flag_showstate:
            print("阵营成员状态:")
            for term in self.members:
                # term.refresh_basevalues()
                term.showstate(full=1,flag_show_max=False)
        return returninfo



class Battle():
    """战斗类，表示一场战斗"""
    def __init__(self,Group1,Group2):  
        self.round=0
        self.winner=None
        self.Groups=[Group1,Group2]
    def Get_All_Units(self):
        lis=[]
        for i in self.order:
            for actor in self.Groups[i].members:
                lis.append(lis)
        return lis     
    def StartBattle(self):
        """开始战斗"""
        self.order=[0,1]
        #先手判定 
        #召唤判定
        #支援判定
        event_onbattlestart(self)
        for i in self.order:
            for actor in self.Groups[i].members:
                actor.in_battle=self
                


        for r in range(1,global_max_rounds):
            self.Start_OneTurn(r)
            if self. winner is not None:
                print("阵营胜利",self.winner,self.Groups[self.winner].Show_Members())
                break
            if r>=global_max_rounds_test:            break
        self.End_Battle()



    def End_Battle(self):
        event_onbattleend(self)
        for i in self.order:
            for actor in self.Groups[i].members:
                actor.End_Battle()
    def Start_OneTurn(self, round_index=1):
        if flag_debuglog:print("开始回合:", round_index)
        event_onturnstart(round_index)
        """开始一轮战斗"""
        if flag_input_in_battle:
            self.Groups[0].Show_Members(flag_showstate=True)
            self.Groups[1].Show_Members(flag_showstate=True)
            input("回合 %d 开始，按回车继续..." %round_index)
        #没有被沉默？
        # self.attack_once(other)
        #反击？
        # other.attack_once(self)
        for i in self.order:
            enemy_group=None
            for op in self.order:
                if op!=i:
                    opponent=op
                    # print(i,opponent,len(self.Groups))[self.order[i]].members
                    enemy_group=self.Groups[opponent]
                    break

            for actor in self.Groups[i].members:
                
                if not enemy_group.Is_Alive():
                    print("阵营%s被消灭" %(opponent),self.Groups[opponent].Show_Members())
                    self.winner=i
                    return 
                enemy_target= enemy_group.members[enemy_group.Frontier()] 
                    
                if actor.Is_Alive() and enemy_target.Is_Alive():    
                    if actor.Is_Stunned():
                        if flag_showinfo_attack: print(strcat(actor.name,"被眩晕，无法行动"))
                        continue
                    #技能
                    returnInfo={}
                    if not (actor.Has_EffectType(EffectType.Mute )or actor.Has_EffectType(EffectType.Stun )):
                        returnInfo=actor.cast_once()
                    # print(returnInfo)

                    if not ("noattack" in returnInfo)  :
                    #普攻
                        
                        actor.cast_attack(enemy_target,state={"round":round_index,"environment":[]})
        self.natural_regenerate()
        event_onturnend(round_index)
        # other.natural_regenerate()
#技能 普通攻击， 对方回合……回复
    def natural_regenerate(self):
        for i in self.order:
            for actor in self.Groups[i].members:
                if actor.Is_Alive():
                    actor.natural_regenerate()


class Actor():
    """角色类，表示一个战斗单位"""
    def __str__(self):
        return "角色:"+str(self.name)
    def __init__(self,name="",baseID=0,health=100,mana=0,level=1,attack=0,defence=0,armor=0,
            atkrate=100,avoid=0,criticalAtk=[1,0,True],block=0,magicresist=0,magicblock=0,healthregen=0,manaregen=0,magicpower=0,
             STRE=0,AGIL=0,INTEL=0,
              gold=0,expgain=0,skilllist=[] ) :
        # print(locals())
        
        self.name=name
        self.baseID=baseID

        for avname, member in ActorValueType.__members__.items():
            # print(name, '=>',ActorValueType[name], member.value)
            a=ActorValue(type_=member,currentvalue=0 if  avname not in locals() else locals()[avname])
            self.__dict__[avname]=a



        self.criticalAtk=criticalAtk # 倍率(单位1.0)，概率（单位1%），第一回合必定暴击？，

        self.skilllist=skilllist


        #active
        self.skilllist_obj=[]
        self.active_spelllist=[]
        self.passive_skilllist=[]
        self.casting_pretime=0
        self.flag_casting=0#0=false ; 1=pre_casting ; 2= 发动技能效果       
        self.parent_group=None
        self.faction=None 
        self.in_battle=False#battle对象
        self.cast_chance=1#可以施法几次
        self.attack_chance=1#可以攻击几次
        

        self.summon=[]
        self.buff_effectlist=[]#魔法效果

        self.related_listener=[]#注册的监听器列表

    def chance_reset(self):
        self.cast_chance=1#可以施法几次
        self.attack_chance=1#可以攻击几次  
        if self.Has_EffectType(EffectType.Stun) or self.Has_EffectType(EffectType.Mute) :
            self.cast_chance=0#可以施法几次
        if self.Has_EffectType(EffectType.Stun) or self.Has_EffectType(EffectType.Disarm) :
            self.attack_chance=0#可以攻击几次  
    def Is_Alive(self):
        return bool(self.health.value>0)
    
    def heal(self,points):
        points=getvalue(points)
        health_1=min(self.health.value+points,self.health.max)
        if (health_1-self.health.value)>0 and flag_showinfo_regen:
            print(strcat(self.name,"恢复",(health_1-self.health.value),"生命值"))
        self.health.value=health_1
    def healmana(self,points):
        points=getvalue(points)
        mana_1=min(self.mana.value+points,self.mana.max)
        if (mana_1-self.mana.value)>0 and flag_showinfo_regen:
            print(strcat(self.name,"恢复",(mana_1-self.mana.value),"魔法值"))
        self.mana.value=mana_1
    def natural_regenerate(self):
        """自然回复生命和魔法值"""
        self.heal(self.healthregen)
        self.heal(self.manaregen)
    def showstate(self,full=False,flag_show_max=False):
        """显示角色状态"""
        if flag_show_max:
            print(self.name, strcat("生命:",self.health),strcat("魔法:",self.mana),strcat("攻击:",self.attack),strcat("防御:",self.defence),)
        else: #getvalue()
            print(self.name, strcat("生命:",getvalue(self.health)),strcat("魔法:",getvalue(self.mana)),strcat("攻击:",getvalue(self.attack)),strcat("防御:",getvalue(self.defence)),)
        if full:
            for k,v in self.__dict__.items():
                if k not in ['health','mana','name','related_listener','in_battle','parent_group','faction','skilllist','skilllist_obj','active_spelllist','passive_skilllist', 'summon']:
                    print(k,'=',getvalue(v),end=', ')
            print()
    def Is_SameGroup(self,targ):
        """判断是否属于同一阵营"""
        return bool(self.parent_group == targ.parent_group)
    def cast_spell(self,spell:Skill,target=None):#  发动技能效果  
        """施放技能"""
        if flag_debuglog>=5: print(strcat(self.name,"施放技能",spell.name))
        # assert spell.skilltype==SkillType.Active
        if target is None:
            if spell.delivery==DeliveryType.Self:
                target=self
            if spell.delivery==DeliveryType.Area:
                target=[]
                battle=self.in_battle
                for actor in battle.Get_All_Units():
                    if TargetPermit.Self in spell.targetpermit  :
                        target.append(self)
                    if TargetPermit.Ally in spell.targetpermit and self.Is_SameGroup(actor) and actor !=self:
                        target.append(actor)
                    if TargetPermit.Enemy in spell.targetpermit and (not self.Is_SameGroup(actor)):
                        target.append(actor)

        targets=To_List(target)
        for effect in  spell.effect_list:
            for targ_ in targets:
                effect_copy=copy.deepcopy(effect)
                effect_copy.Apply(self,targ_)
                global_observer_list.append( effect_copy)#注册观察者
    def get_current_spell(self) -> Skill: 
        """获取当前施放的技能"""
        if len(self.active_spelllist)>0:
            for spell in self.active_spelllist:
                if spell.ammunition.currentvalue>0:
                    return spell
            return self.active_spelllist[0]
        return None
    def cast_once(self):
        """施放一次主动技能"""
        spell=self.get_current_spell()
        if spell is not None:
            spell.ammunition.ModValue(-1,zerobound=True) #消耗弹药
            if spell.casting_pretime>1:#施法中  打断则无法再次蓄力
                spell.casting_pretime-=1      
                return  {"noattack":True}#popout
            while (len(self.active_spelllist)>=1):
                spell=self.active_spelllist[0]
                # spell=Skill()
                assert spell.skilltype==SkillType.Active
                # if 

                # self.cast_once()
                self.casting_pretime=spell.casting_pretime
                # if  
    #如果则
            if spell.allow_attack:
                return {}
        return {}#pop the spell
    def cast_attack(self,other,state={"round":1,"environment":[]},flag_rounds=True):
        """发动普通攻击"""
        physicaldamage=Apply_Damage(other,self.attack.value,self=self,damagetype=DamageType.Physical,state=state,flag_rounds=flag_rounds)
        if flag_showinfo_attack: print(strcat(self.name,"对",other.name,"造成",physicaldamage,"伤害"))
        # other.ModActorValue(ActorValueType.health,-physicaldamage) 
        
        return (physicaldamage)
    def Is_Stunned(self):
        """检查是否被眩晕"""
        stunned=False
        for buff in self.buff_effectlist:
            if buff.archetype==EffectType.Stun:
                stunned=True
        return stunned
    def Has_EffectType(self,typ:EffectType):
        """检查是否有指定类型的魔法效果"""
        hastype=False
        for buff in self.buff_effectlist:
            if buff.archetype==typ :
                hastype=True
        return hastype
    # def Has_Effect(self,eff:Effect):
    #     haseff=False
    #     for buff in self.effect_list:
    #         if buff ==eff :
    #             haseff=True
    #     return haseff
    def Has_EffectId(self,effid):
        """检查是否有指定ID的魔法效果"""
        haseff=False
        for buff in self.buff_effectlist:
            if buff.baseID ==effid :
                haseff=True
        return haseff
    def End_Battle(self):
        """结束战斗，清除战斗状态"""
        self.in_battle=False
        # self.parent_group=None
        #dispell
        for buff in self.buff_effectlist:
            if buff is None:
                self.buff_effectlist.remove(buff)
                print("warning: buff is None",self.name)
            else:
                if buff.dispell_after_battle:
                    buff.Dispell()
                else:
                    print("保留buff:",buff.name,self.name)
    def instantiate(self):
        """实例化角色，返回一个新的角色对象"""
        aaa= copy.deepcopy(self)  
        # aaa.__class__=ActorRef
        return aaa
    def ModActorValue(self,avtype:ActorValueType,value ,maxbound=None,zerobound=False,**kwargs): 
        """修改角色属性值"""
        if isinstance(avtype,ActorValueType):avtype=avtype.name
        maxbound=DefaultValue_If_None(maxbound,True if avtype in AVhasMaxList else False)

        return self.__dict__[avtype].ModValue(value=value ,maxbound=maxbound,zerobound=zerobound)
    def ModActorPeakValue(self,avtype:ActorValueType,value,flag_proportion=True,flag_clipup=True,**kwargs): 
        """修改角色属性峰值"""
        if isinstance(avtype,ActorValueType):avtype=avtype.name
        self.__dict__[avtype].ModPeakValue(value=value ,flag_proportion=flag_proportion,flag_clipup=flag_clipup)
    def GetActorValuePercentage(self,avtype:ActorValueType ): 
        """获取角色属性的百分比"""
        if isinstance(avtype,ActorValueType):avtype=avtype.name
        return self.__dict__[avtype].get_percentage()
    def GetActorValue(self,avtype:ActorValueType ): 
        """获取角色属性值"""
        if isinstance(avtype,ActorValueType):avtype=avtype.name
        return self.__dict__[avtype].currentvalue

    def deal_skillList(self):
        """处理角色的技能列表，将技能ID和参数转换为技能对象列表"""
        reader_pointer=0
        skillList=[]
        lis=self.skilllist if isinstance(self.skilllist,list) and len(self.skilllist)==2 else [[],[]]
        for id in lis[0]:
            skill=copy.deepcopy(global_SkillList[id]) 
            # print(skill.description)
            skill.parameters=lis[1][reader_pointer].copy()   if len(lis[1])>reader_pointer else []  
            # if len(lis[1])<=reader_pointer:
                # print(self.name,"技能参数不足",skill.name,lis)
            if "\\v" in skill.description:
                temp=skill.description.split("\\v")
                # print(lis[1][reader_pointer])
                joins=temp[0]
                for i in range(len(temp)-1):
                    if len(lis[1])<=reader_pointer:
                        print(self.name,"技能参数不足",skill.name,lis)
                        break
                    if i ==len(temp)-2 and len(lis[1][reader_pointer][i:])>1:
                        joins=joins+str(lis[1][reader_pointer][i:])+temp[i+1]
                    else:
                        if i >=len( lis[1][reader_pointer] ):
                            joins=joins+"0"+temp[i+1]
                            print("warning skill param len",self.name,skill.name,lis)
                        else:
                            joins=joins+lis[1][reader_pointer][i]+temp[i+1]
                skill.description=(joins)
                reader_pointer+=1
            skill.process_skill_effects()


            skillList.append(skill)
        self.skilllist_obj=skillList
        self.active_spelllist=[term for term in self.skilllist_obj if term.skilltype==SkillType.Active]
        self.passive_skilllist=[term for term in self.skilllist_obj if term.skilltype==SkillType.Passive]
    def refresh_basevalues(self,recal_buff=True):
        """刷新角色的基础属性值"""
        for avname, member in ActorValueType.__members__.items() :
            # print(name, '=>',ActorValueType[name], member.value)
            if member not in AVhasMaxList:
                self.__dict__[avname].currentvalue=self.__dict__[avname].basevalue
            else:
                diff=self.__dict__[avname].maxvalue -self.__dict__[avname].basevalue
                self.__dict__[avname].ModPeakValue(-diff)
                # self.__dict__[avname].currentvalue=self.__dict__[avname].basevalue
                # a=ActorValue(type_=member,currentvalue=.basevalue,maxvalue=self.__dict__[avname].basevalue,basevalue=self.__dict__[avname].basevalue)
                # self.__dict__[avname]=a
        if recal_buff:
            for effect in self.buff_effectlist:
                if not effect.is_amount_modifier():
                    effect.Enforce( )
    def check_passive_skills(self):
        """检查并触发被动技能效果"""
        for listener in self.related_listener:
            remove_all_related_listeners(  listener)
        self.related_listener=[]#清空监听器列表，重新注册
        self.check_passive_skills_selfbuff()
        self.check_passive_skills_onattack( )
    def check_passive_skills_selfbuff(self):##       【记得注意注册时机、状态刷新、和取消注册！！】
        """检查并触发被动技能效果"""
        dispatch_event("OnActorStateChange", actor=self, reason="recheck")
        for skill in self.passive_skilllist:
            if skill.skilltype==SkillType.Passive and skill.delivery==DeliveryType.Self:
                for effect in skill.effect_list:
                    effect_copy=copy.deepcopy(effect)
                    effect_copy.Apply(self,self)

    def check_passive_skills_onattack(self  ):##       【记得注意注册时机、状态刷新、和取消注册！！】
        """检查并触发被动技能效果"""
        for skill in self.passive_skilllist:
            if  skill.skilltype==SkillType.Passive and skill.delivery==DeliveryType.Contact:
                listener=Listener(event_name="OnRecordDamage", callback=self.cast_spell,
                    condition_kwargs={"source":self},#, "target":targ
                                  spell=skill,target=EvtKwarg("target") )
                add_listener("OnRecordDamage",  listener)
                self.related_listener.append(listener)
    def __del__(self):#析构函数
        """删除角色，取消注册所有监听器，将自身化为None"""
        #删除全部魔法效果、状态效果
        for effect in self.buff_effectlist:
            effect.Dispell()
        for listener in self.related_listener:
            remove_all_related_listeners(  listener)
        self.related_listener=[]
        #Noneify
        del self



#事件系统: 事件-条件-动作
class Event():
    """事件类，表示一个游戏事件"""
    ##
    def __init__(self,name="",**kwargs):
        self.name=name
        self.kwargs=kwargs
    def __str__(self):
        return "事件:"+str(self.name)
class Listener():
    """监听器类，表示一个事件监听器"""
    def __init__(self,event_name="",callback=None,condition_kwargs=None,**kwargs):
        self.event_name=event_name
        self.callback=callback
        self.condition_kwargs=condition_kwargs
        self.kwargs=kwargs
class EventRespond(Enum):
    Empty=0
class EvtKwarg():
    """事件关键字参数类，表示一个事件的关键字参数"""
    def __init__(self,keyname ):
        self.keyname=keyname

def Apply_Damage(targ : Actor,damage=0,flag_aftertex=False,self=None  ,damagetype=DamageType.Physical
        ,state={"round":1,"environment":[]},flag_rounds=True ):
    """应用伤害"""
    v=damage
    if damagetype==DamageType.Physical:
        v=cal_phy_damage(v,self,targ,state,flag_rounds=flag_rounds)
         
    
    elif  damagetype==DamageType.Physical:
        v=cal_magic_damage(v,self,targ,state)
    elif  damagetype==DamageType.Poison:
        v=cal_poison_damage(v,self,targ,state)
    else:
        v=v
    event_record_damage(v,self,targ,damagetype,state)

    targ.ModActorValue(avtype=ActorValueType.health,value=-v)
    return v
def cal_phy_damage(v,self : Actor,targ : Actor,state={"round":1,"environment":[]} ,flag_rounds=True):
    """计算物理伤害"""
    v=DefaultValue_If_None(v,self.attack)
    v=AD(v,targ.defence)
    v=v*factor_armor(targ.armor)
    v=AD(v,targ.block)
    if flag_rounds:
        v=v*factor_avoid(targ.avoid)*factor_attackrate(self.atkrate)*factor_critical(self.criticalAtk,is_r1=state['round']==1)
    
    return v
def cal_magic_damage(v,self : Actor,targ : Actor,state={"round":1,"environment":[]}):
    """计算魔法伤害"""
    v=v*factor_magicresist(targ.magicresist)
    v=AD(v,targ.magicblock)
    return v
def cal_poison_damage(v,self : Actor,targ : Actor,state={"round":1,"environment":[]}):
    """计算毒素伤害"""
    v=v*factor_armor(targ.armor)
    v=AD(v,targ.block)
    return v
def cal_custom_damage(v,self : Actor,targ : Actor,state={"round":1,"environment":[]}):
    return eval("v")
def load_value(v,int_if_approchint=True):
    if isinstance(v,str)  :
        v=float(v)
    try:
        if int_if_approchint and abs(v-int(v))<1e-6:
            v=int(v)
    except:
        pass
    return v
class Effect():

    def __str__(self):
        return "效果:"+str(self.name)
    """魔法效果类，表示一个魔法效果"""
    def __init__(self,name="",baseID=0,magnitude=0,duration=0
                 , archetype=EffectType.Empty,max_stack=1,
                 trigger_on_battle_start=False,dispell_after_battle=True,dispell_onstatechange=False,trigger_on_apply=None,recover_on_remove=None,trigger_on_turn_start=None,
                 keywords_stack=None,associatedItem=None,target=None,caster=None,evalfunstr="value"):#stack=Stack
        self.name=name
        self.baseID=baseID
        self.magnitude=load_value(magnitude)
        self.duration=load_value(duration)
        self.rest_duration=load_value(duration)
        # self.rest_duration=self.duration
        self.archetype=EnumConvert(EffectType, archetype)
        self.max_stack=max_stack
        self.keywords_stack=keywords_stack

        self.target=target
        self.caster=caster


        self.active=False
        self.dispell_after_battle=dispell_after_battle
        self.trigger_on_battle_start=trigger_on_battle_start
        self.dispell_onstatechange=dispell_onstatechange


        #这几项需要自定义
        self.associatedItem=EnumConvert(ActorValueType, associatedItem)
        if evalfunstr is None or evalfunstr=="" or (isinstance(evalfunstr,float) and math.isnan(evalfunstr)):
            evalfunstr="value"
        self.evalfunstr=evalfunstr 
        self.kwargs={}
        self.extra_custom_scripts=[]

        maybe_damage_heal=False
        maybe_damage_heal = self.is_amount_modifier()

        self.trigger_on_apply = DefaultValue_If_None(trigger_on_apply, True )
        self.trigger_on_turn_start = DefaultValue_If_None(trigger_on_turn_start, maybe_damage_heal )
        self.recover_on_remove = DefaultValue_If_None(recover_on_remove, not maybe_damage_heal )

        self.related_listener=[]#注册的监听器列表
    def evalfun(self,value,caster:Actor,target:Actor):
        return eval(self.evalfunstr,globals(),locals())
    def is_amount_modifier(self):
        maybe_damage_heal=self.associatedItem in AVhasMaxList and self.archetype in [EffectType.ValueModifier ]
        return maybe_damage_heal
    def showinfo(self):
        print(f"效果名称: {self.name}")
        print(f"效果类型: {self.archetype}")
        print(f"效果强度: {self.magnitude}")
        print(f"效果持续时间: {self.rest_duration} / {self.duration}")
        print(f"效果最大层数: {self.max_stack}")
        print(f"效果关键字: {self.keywords_stack}")
        print(f"效果关联属性: {self.associatedItem}")
        print(f"效果trig_recover: {self.trigger_on_apply},{self.trigger_on_turn_start},{self.recover_on_remove}")
    def Apply(self,caster:Actor,target:Actor):
        """应用魔法效果"""
        if flag_debuglog>=3: print(f"施法者: {caster.name}, 目标: {target.name}, 效果: {self.name}"  )
        self.caster=caster
        self.target=target
        self.rest_duration=self.duration
        self.value=self.evalfun( self.magnitude,caster,target)
        #check self.max_stack
        if target.Has_EffectId(self.baseID):
            #找到已有效果
            # for eff in target.buff_effectlist:
            sublist=[eff for eff in target.buff_effectlist if eff.baseID == self.baseID]
            # if eff.baseID == self.baseID:
                #检查数量，如果不足max_stack则添加一个，如果满了则刷新持续时间
            if len(sublist)<self.max_stack:
                #添加一个新的效果，走后面的逻辑
                pass
            else:#刷新第一个的持续时间！！【注意仅供测试 不合理！！】应该顶掉最弱的
                for eff in sublist:
                    eff.Refresh()
                    return


        if self.rest_duration>0:#施加buff列表
            self.active=True
            self.target.buff_effectlist.append(self)

        #event trigger 
        if self.trigger_on_apply:
            listener=Listener(event_name="OnEffectStart", callback=Effect.Enforce, #写法1
                                                   condition_kwargs={"caster":caster, "target":target,"effect":self} ) 
            listener.kwargs =dict( self=self ,caster=caster,target=target,effect=self)#都是必要的
            add_listener("OnEffectStart",  listener)
            self.related_listener.append(listener)
        if self.trigger_on_turn_start:
            listener=Listener(event_name="OnTurnStart", callback=Effect.Enforce, #写法1
                                                   condition_kwargs={ })
            listener.kwargs =dict( self=self ,caster=caster,target=target,effect=self)#除了self=self其他的都暂时冗余但是不报错
            add_listener("OnTurnStart",   listener  )
            self.related_listener.append(listener)
        if True:#turn end  - Elapse
            listener=Listener(event_name="OnTurnEnd", callback=Effect.Elapse, 
                                                   condition_kwargs={ })
            listener.kwargs =dict( self=self )
            add_listener("OnTurnEnd",   listener  )
            self.related_listener.append(listener)
        if self.recover_on_remove:
            listener=Listener(event_name="OnEffectEnd", callback=Effect.Recover ,
                              condition_kwargs={"effect":self} )
            listener.kwargs =dict( self=self ,effect=self )#除了self=self其他的都暂时冗余但是不报错
            add_listener("OnEffectEnd",  listener)
            self.related_listener.append(listener)
        if self.dispell_onstatechange:
            listener=Listener(event_name="OnActorStateChange", callback=Effect.Dispell ,
                              condition_kwargs={"actor": target,"reason":"recheck"} )
            listener.kwargs =dict( self=self ,reason="recheck" )#info recheck
            add_listener("OnActorStateChange",  listener)
            self.related_listener.append(listener)
        event_oneffectstart(caster=caster,target=target,effect=self)

    def Refresh(self):
        """刷新魔法效果"""
        self.rest_duration=self.duration
    
    def Elapse(self):
        """时间流逝，减少持续时间"""
        self.rest_duration-=1
        if flag_debuglog>=4: print("效果持续时间减少:",self.name,self.rest_duration)
        if self.rest_duration<=0:
            if flag_debuglog>=2: print("效果持续时间结束，驱散效果:",self.name)
            self.Dispell()
    def Dispell(self,**kwargs):
        """驱散魔法效果"""
        for eff in self.target.buff_effectlist:
            if eff == self:
                self.target.buff_effectlist.remove(eff)
                #删除效果
        self.active=False
        # self.caster=None
        # self.target=None
        # self.rest_duration=0
        event_oneffectend(caster=self.caster,target=self.target,effect=self)
        for listener in self.related_listener:
            remove_all_related_listeners(listener)

    def Enforce(self,**kwargs):  #注意这里只能修改actorvalue，否则会乱套
        """魔法效果生效"""
        if flag_debuglog>=3: print("效果生效:",self.name,self.value)
        if self.archetype==EffectType.ValueModifier:
            self.target.ModActorValue(avtype=self.associatedItem,value=self.value,** kwargs)
        if self.archetype==EffectType.PeakValueModifier:
            self.target.ModActorPeakValue(avtype=self.associatedItem,value=self.value,** kwargs)

    def Recover(self,**kwargs):
        """恢复数值"""
        if flag_debuglog>=4: print("效果结束后恢复:",self.name)
        if self.archetype==EffectType.ValueModifier:
            self.target.ModActorValue(avtype=self.associatedItem,value=-self.value,** kwargs)
        if self.archetype==EffectType.PeakValueModifier:
            self.target.ModActorPeakValue(avtype=self.associatedItem,value=-self.value,** kwargs)
def str2list(s):
    rtv=[]
    if  isinstance(s,str) :
        rtv=s.split(",")
        rtv=[ (id) for id in rtv]
    return rtv
def loadskill(dic):
    rtv=[]
    params=[]
    if  isinstance(dic['SkillList'],str) :
        rtv=dic['SkillList'].split(",")
        rtv=[int(id) for id in rtv]
    if  isinstance(dic['SkillParameters'],str) :
        params=dic['SkillParameters'].split(",")
        params=[id.split("-") for id in params]
    return [rtv,params]
def readskill(lis,):
    reader_pointer=0
    for id in lis[0]:
        skill=global_SkillList[id]
        # print(skill.description)
        if "\\v" in skill.description:
            temp=skill.description.split("\\v")
            # print(lis[1][reader_pointer])
            joins=temp[0]
            for i in range(len(temp)-1):
                if i ==len(temp)-2 and len(lis[1][reader_pointer][i:])>1:
                    joins=joins+str(lis[1][reader_pointer][i:])+temp[i+1]
                else:
                    joins=joins+lis[1][reader_pointer][i]+temp[i+1]
            print(joins)
            reader_pointer+=1

def postset(id,health,attack,defence,atkrate,armor=0,gold=None,exp=None):
    global global_MonsterBaseList
    id=id
    global_MonsterBaseList[id].health=ActorValue(type_=ActorValueType.health,currentvalue=int(health))
    global_MonsterBaseList[id].attack=ActorValue(type_=ActorValueType.attack,currentvalue=int(attack))
    global_MonsterBaseList[id].defence=ActorValue(type_=ActorValueType.defence,currentvalue=int(defence))
    global_MonsterBaseList[id].atkrate=ActorValue(type_=ActorValueType.atkrate,currentvalue=int(atkrate))
    if armor !=0:
        global_MonsterBaseList[id].armor=ActorValue(type_=ActorValueType.armor,currentvalue=int(armor))
    if gold:
        global_MonsterBaseList[id].gold=int(gold)
    if exp:
        global_MonsterBaseList[id].expgain=int(exp)
def postset_bat():
    """设置战斗单位的属性"""
    global global_MonsterBaseList
    postset(998,400000,50000,30000,100,0) 
    postset(997,4000000000,500000000,300000000,100,0)

    postset(878,760000000,108000000,45000000,12500,240) #蓑衣处刑者
    postset(877,536000000,78000000,44000000,10000,300) #神弃信徒
    postset(876,120000000,72000000,65000000,1500,2000) #萨弗尔格雷姆
    postset(875,560000000,75000000,50000000,8500,275) #秘仪护教军团
    postset(874,750000000,60000000,60000000,8000,350,15000,3000000) #伊贝伦族长
    postset(873,750000000,90000000,40000000,12000,270,15000,3000000) #索雷斯族长    
    postset(872,250000000,75000000,45000000,7000,280) #圣夜守护长老
    postset(871,440000000,65000000,45000000,25000,300) #伊贝伦近卫队
    postset(870,350000000,50000000,35000000,20000,300) #伊贝伦护卫队
    postset(869,510000000,60000000,48000000,9600,290) #圣夜秘仪帝皇
    postset(868,270000000,80000000,32000000,15000,320) #圣夜裁决者
    postset(867,200000000,85000000,25000000,12000,300) #具现化月蚀
    postset(866,270000000,50000000,45000000,5000,280) #日曜守护长老
    postset(865,40000000,60000000,60000000,1500,2000) #奥克弥格雷姆
    postset(864,440000000,62000000,46000000,7500,300) #索雷斯护卫队
    postset(863,240000000,75000000,38000000,7000,450) #基恩督查者
    postset(862,500000000,56500000,40000000,4800,330) #圣夜护教军团
    postset(861,250000000,68000000,38000000,7200,500) #基恩镇域者
    global_MonsterBaseList[860].name="哈玛·索雷斯:1000-8000000:7-7-200000000-50000000:5-3-15-400&1"
    postset(860,620000000,75000000,36000000,10000,340,10000,2000000) #哈码·索雷斯
    postset(859,350000000,48000000,36500000,6000,300) #索雷斯近卫队
    postset(858,420000000,46500000,30000000,4800,330) #光耀护教军团
    postset(857,180000000,56000000,27000000,6000,450) #基恩监视者
    postset(856,200000000,52000000,25000000,8100,450) #基恩主战者
    postset(855,235000000,50000000,24000000,10800,325) #绝对忠诚近卫
    postset(854,500000000,75000000,40000000,12000,310) #终阶圣堂武士
    postset(853,485000000,84000000,38000000,11000,320) #巴巴托斯
    global_MonsterBaseList[852].dex=1002
    global_MonsterBaseList[852].name="圣夜之子-苍真:5-3:25-50:5-20-100000000"
    postset(852,300000000,68000000,38000000,9000,350,25000,5000000) #圣夜之子-苍真
    postset(851,800000000,0,0,10000,250) #边缘之影
    postset(850,235000000,45000000,24000000,10800,325) #绝对忠诚近卫
    global_MonsterBaseList[849].dex=1002
    global_MonsterBaseList[849].name="光耀之子-西蒙:5-3:25-50:10-100000000-20000000-5000000"
    postset(849,200000000,56000000,32000000,9000,350,25000,5000000) #光耀之子-西蒙
    postset(848,360000000,108000000,33000000,7500,200) #链弱魔
    postset(847,450000000,90000000,36000000,9500,270) #圣堂刽子手
    global_MonsterBaseList[846].name="天国恩赐战甲:10-5-3:10-10000000-5000000-5000000"
    postset(846,580000000,55000000,45000000,8500,400) #天国恩赐战甲
    global_MonsterBaseList[845].name="圣堂护教军团:4200000:5-200000000-3000-50:2-10"
    postset(845,245000000,42500000,22000000,4000,320) #圣堂护教军团
    postset(844,280000000,38000000,20000000,4000,360) #枢机近卫队
    postset(843,200000000,45000000,25000000,7500,300) #霍尔蒙克斯
    postset(842,300000000,80000000,20000000,12000,275) #液态光2
    postset(841,340000000,36000000,26800000,9000,280) #圣光祭司君王
    postset(840,268000000,39000000,22000000,8000,300) #神选信徒
    postset(839,375000000,40000000,35000000,5400,250) #圣光唱诗班
    postset(838,450000000,45000000,30000000,7200,350) #高阶龙鳞主教
    postset(837,450000000,50000000,30000000,5000,250) #高阶狮心主教
    global_MonsterBaseList[836].dex=1002
    global_MonsterBaseList[836].name="阿珐莉娅:8000000:5-160000000:10-2500-330000000-500000000"
    postset(836,360000000,36000000,20000000,10000,240,10000,2000000) #小蓝帽
    global_MonsterBaseList[835].dex=1002
    postset(835,400000000,45000000,21000000,15000,250,10000,2000000) #阿尔西斯
    postset(834,7000000000,132000000,83000000,30000,250,50000,25000000) #特拉希尔意志
    postset(833,900000000,85000000,48000000,14000,360) #高阶戒律主教
    postset(832,450000000,32500000,25000000,25000,300) #赫尔奥沙
    postset(831,268000000,28500000,21500000,8000,260) #白夜妖精术士
    global_MonsterBaseList[831].name="白夜妖精术士:7200000:5-5-30:10-250000000-5-300"
    postset(830,232000000,33000000,19800000,3200,280) #白夜妖精猎手
    postset(829,165000000,32000000,14800000,13500,300) #迅猛桀派
    postset(828,265000000,48000000,22000000,9000,260) #白夜潜伏者
    postset(827,960000000,85000000,45000000,16000,420) #高阶枢机仲裁
    postset(826,3000000000,40000000,20000000,16000,100,10000,2000000) #狂性之瑞普
    global_MonsterBaseList[826].magicresist=-100
    postset(825,400000000,42500000,32000000,6000,280,10000,2000000) #呼啸之布雷兹
    postset(824,800000000,35000000,12500000,5000,150) #科伯尔狂热者
    postset(823,40000000,30000000,15000000,1200,1500) #萨弗尔格雷姆
    postset(822,275000000,24000000,19800000,9000,280) #圣光术士君王
    postset(821,288000000,33600000,15800000,16000,300) #律迹汜幂
    postset(820,333000000,22800000,11000000,4000,290) #曼德拉克聚落
    postset(819,228000000,26000000,16000000,7700,360) #格兰尼特地龙
    postset(818,200000000,50000000,10000000,9000,250) #业态光
    postset(817,420000000,56000000,36000000,6400,270) #白夜精灵司祭
    global_MonsterBaseList[817].name="白夜妖精司祭:4800000:7-7-150:8-5000000:8-50-500000-2.5"
    postset(816,250000000,30000000,20000000,7200,350) #龙鳞主教
    postset(815,440000000,60000000,18000000,11000,300,5000,1000000) #狂暴之索尔
    postset(814,150000000,35000000,12000000,8500,350,5000,1000000) #坚盾之索尔
    postset(813,250000000,40000000,12000000,6500,290) #不屈卫尔特斯
    postset(812,50000000,30000000,12000000,6500,250) #刚毅卫尔特斯
    postset(811,150000000,44000000,11000000,7500,200) #双昼灵
    postset(810,240000000,26500000,17500000,3500,300) #晴雪城卫队
    postset(809,250000000,32000000,18500000,5000,250) #狮心主教
    postset(808,360000000,45000000,25000000,15000,350) #安戈洛执政官
    postset(807,215000000,18000000,14000000,9000,280) #圣光术士兵团
    postset(806,144000000,24000000,10000000,10000,300) #圣魂战甲兵团
    postset(805,172000000,22000000,13000000,8000,320) #魔导战甲兵团
    global_MonsterBaseList[804].dex=1002
    postset(804,450000000,21000000,12000000,15000,250,0,2000000) #阿尔西斯

    global_MonsterBaseList[802].maxsp=20000
    global_MonsterBaseList[802].dex=1003
    postset(802,420000000,30000000,16000000,27000,240,50000,1000000) #无名
    postset(801,100,15000000,22500000,10000,0) #远古赏金神符
    global_MonsterBaseList[800].maxsp=12000
    global_MonsterBaseList[800].dex=1003
    postset(800,420000000,26500000,13500000,17600,240,50000,1000000) #血湮
    postset(799,200000000,24000000,13600000,11000,240) #无间业火道兵
    postset(798,200000000,20000000,12500000,9000,200) #玲珑凰儡
    postset(797,180000000,17600000,13600000,3000,180) #酣巨人豢兵
    postset(796,308000000,21000000,16800000,10000,150) #天虞冰夷
    postset(795,150000000,24000000,15000000,5000,200) #西烈诸犍
    postset(794,176000000,25000000,17500000,500,200) #盘瓠氏少年
    postset(793,70000000,32000000,7800000,5000,155) #夕死者
    postset(792,450000000,19800000,11800000,25000,250)
    global_MonsterBaseList[792].name="无影的炼:1-80:85000000-10:3:30000000-150000000&1"
    global_MonsterBaseList[792].dex=1003
    postset(791,200000000,20000000,12500000,9000,200) #玲珑凰儡
    postset(749,350000000,25000000,12000000,25000,300) #赤阳
    global_MonsterBaseList[749].name="赤■仙■:1-80:50-200:250000000-50-30-20"
    global_MonsterBaseList[749].dex=1003
    postset(790,200000000,24000000,13600000,8000,240) #无间业火道兵
    postset(789,155000000,16500000,11000000,3600,210) #三生凰儡
    postset(788,120000000,17500000,10500000,5000,185) #大衍寓鸟
    postset(787,140000000,16800000,9600000,5500,240) #神垕骁骑
    postset(786,145000000,21000000,14500000,7200,225) #枉死星君
    postset(785,500000000,20000000,10000000,5500,225) #神垕古皇
    global_MonsterBaseList[784].name="鑫火帝君:3000000:1-150:9-9-80000000-5000000:30-200"
    postset(784,500000000,18500000,13500000,8000,250) #鑫火帝君
    postset(783,135000000,17000000,8000000,8000,235) #天人阿修罗
    postset(782,150000000,15000000,12500000,4500,160) #司辰巫士
    postset(781,180000000,18500000,12000000,7500,220) #玄都玉驹
    postset(780,80000000,17800000,9500000,12100,225) #姑逢獙獙
    postset(779,135000000,13500000,11000000,5000,230) #拜火大司
    postset(778,96000000,14200000,11800000,2500,200) #无垢仙灵
    postset(777,150000000,16000000,12000000,3600,250) #神垕图腾
    postset(776,100000000,14500000,10800000,4800,300) #大焚星君
    postset(775,150000000,16000000,12000000,3600,250) #玄冥图腾
    postset(774,125000000,15600000,11000000,7000,200) #南明离火
    postset(773,135000000,17600000,8000000,7000,200) #九幽玄火
    postset(772,120000000,14800000,11000000,3000,250) #天吴图腾
    postset(771,115000000,11500000,9000000,5000,220) #拜火少司

    postset(770,135000000,14500000,9000000,3600,210) #三生凰儡
    postset(769,125000000,15600000,11000000,7000,200) #南明离火
    postset(768,140000000,16800000,9600000,5500,240) #神垕骁骑
    postset(766,120000000,17500000,10500000,5000,185) #大衍寓鸟
    global_MonsterBaseList[765].name="煌叶林海司祭:4000000:5-5-1:7-7-500:100-2"
    postset(765,96000000,12000000,7500000,4500,200) #煌叶林海司祭
    postset(764,110000000,12000000,10000000,10000,250) #林海相柳
    postset(763,85000000,14200000,8800000,400,120) #归墟噩梦
    postset(762,80000000,11000000,9000000,5000,190) #玉京仙灵
    postset(761,68000000,14500000,7800000,4000,200) #血滴子
    postset(760,75000000,13500000,8500000,3500,220) #碧落冥卫
    postset(758,70000000,10800000,6400000,5000,175) #涿光寓鸟
    postset(757,90000000,9500000,7000000,4500,220) #往生冥卫
    postset(756,105000000,12000000,7500000,7200,220) #上级贪狼道兵
    postset(755,75000000,11000000,6200000,7000,225) #赤水蠃鱼
    postset(754,96000000,10000000,8000000,6400,235) #宁海长右巨兽
    postset(753,120000000,11500000,3800000,22500,180) #巴蛇幼仔
    postset(752,72000000,8500000,6500000,3500,210) #上级天策道兵
    postset(751,85000000,10500000,6800000,5000,230) #上级羽灵道兵

    postset(748,2440000000000,220000000000,78000000000,250000,2800) #镇界行龙
    postset(747,96000000,15000000,8000000,6400,235) #混沌宁海长右
    postset(746,113500000,13500000,7700000,10800,225) #祖灵宁海长右
    global_MonsterBaseList[745].dex=1003
    postset(745,168000000,14400000,8800000,4000,250,0,3000000) #XC
    global_MonsterBaseList[744].dex=1003
    global_MonsterBaseList[744].name="米斯特瑞德:3650000-3-50:8-15-1000000000"
    postset(744,225000000,16800000,9600000,10000,230,0,3000000) #米斯特瑞德
    postset(743,165000000,22500000,10000000,12500,240) #无面尸祖
    global_MonsterBaseList[742].dex=1003
    postset(742,130000000,13600000,8400000,7200,220,0,3000000) #迪迦基
    global_MonsterBaseList[741].dex=1003
    global_MonsterBaseList[741].name="训仙鸿:1-1-50:7-25000000-3-50:30-30:1000-15&1"
    postset(741,320000000,23500000,12500000,16800,230,50000,1000000) #训仙鸿
    postset(740,150000000,12000000,5000000,10000,250) #煌叶太安功曹
    postset(739,65000000,8500000,2400000,6000,240) #煌叶奇袭道兵
    postset(738,68000000,5800000,4200000,5000,210) #煌叶天玄密宗
    postset(736,80000000,7500000,3700000,8000,210) #煌叶绝杀道兵
    postset(735,80000000,6500000,4800000,4500,280) #煌叶守御道兵
    global_MonsterBaseList[737].name="塞缇娜:4:5-5-1000:20-80000000-2-40:15-160000000-3-250"
    postset(737,110000000,10800000,6250000,7500,250,0,3000000) #塞缇娜
    global_MonsterBaseList[737].dex=1002
    postset(734,120000000,9500000,4500000,6000,185,0,3000000) #达戈诺娃
    global_MonsterBaseList[734].dex=1002
    postset(732,150000000,5000000,3500000,9000,238) #多智龙王
    postset(731,50000000,4300000,2000000,6000,200) #乳齿巨像
    postset(730,10000000,5800000,3000000,7500,200) #无齿翼龙
    postset(728,60000000,4000000,2500000,8000,150) #巨鳄勇士
    postset(727,90000000,7000000,4800000,11000,250,0,3000000) #尤洛瑞
    global_MonsterBaseList[727].dex=1002
    postset(725,55000000,7500000,4500000,7500,225) #无面尸尊
    postset(724,100000000,8000000,4000000,4500,200) #司彘图腾
    postset(723,20000000,5500000,3000000,5000,150) #司彘长右司祭
    postset(722,50000000,6500000,2500000,5000,150) #司彘长右巨兽
    postset(721,35000000,5800000,3200000,5000,160) #司彘长右勇士
    postset(720,80000000,5000000,3000000,7000,175) #叉西大哥
    postset(719,25000000,6000000,3000000,5000,160) #司彘长右
    postset(718,70000000,5870000,3450000,8000,270,0,3000000) #布伦希尔德
    global_MonsterBaseList[718].name="布伦希尔德:30000000:7-7-15000000-2500000:9-9-5-50000000-3"
    global_MonsterBaseList[718].dex=1002
    postset(717,40000000,9000000,6000000,6500,225) #索魂灵王
    postset(716,32000000,10500000,5800000,4400,210) #夜魅幼体
    postset(715,45000000,9500000,5600000,7500,220) #煌叶赤水督军
    postset(714,200000000,9000000,4000000,40000,150) #何罗之鳝
    global_MonsterBaseList[714].name="何罗之鳝:10-500000000-300000000:50-200-99&1"
    postset(713,50000000,7600000,5000000,3500,240) #昆仑道兵
    postset(712,43500000,8900000,4350000,8800,225) #宁海长右勇士
    postset(711,40000000,0,4500000,4200,210) #厉角巫祭
    postset(710,45000000,8500000,4000000,6000,225) #古代阿修罗
    postset(709,42000000,8100000,3700000,5800,210) #中级贪狼道兵
    postset(708,36000000,6500000,4200000,3300,220) #精锐赤龙战甲
    postset(707,38000000,5800000,4500000,4000,210) #复社巫徒
    postset(706,50000000,7200000,4000000,4500,200) #帝释凰儡
    postset(705,42000000,7500000,2800000,2500,200) #杀星凰儡
    postset(704,33000000,6800000,3800000,7200,230) #破虚战甲
    postset(703,35000000,7000000,3000000,8400,208) #延维幼仔
    postset(702,36000000,5800000,3600000,7800,225) #宁海长右
    postset(701,45000000,4400000,3400000,2800,150) #酣巨人奴仆
    postset(700,30000000,5500000,2500000,8000,215) #奉贤殿侍从
    postset(699,20000000,7700000,1800000,4000,175) #朝闻道者
    postset(698,24000000,6000000,2750000,5500,210) #中级破军道兵
    postset(697,35500000,4200000,3000000,3000,200) #中级天策道兵
    postset(696,32000000,5100000,3300000,4500,210) #中级羽灵道兵
    postset(695,60000000,4770000,1440000,19600,290,0,3000000) #欧洛巴士2
    global_MonsterBaseList[695].dex=1002
    postset(694,50000000,5000000,2400000,12000,250,0,5000000) #猰貐真灵
    global_MonsterBaseList[694].name="猰貐真灵:2-100:13-13-50:13-13-50:13-13-100"
    postset(691,40000000,3500000,1800000,3000,210) #无面尸佛
    global_MonsterBaseList[691].name="无面尸佛:692-Monster15+01&4&250:0-1:5-5-5000000"
    postset(690,54000000,5000000,2450000,5500,200) #煌叶绝杀道兵
    postset(689,54000000,4360000,3250000,3000,270) #煌叶守御道兵
    postset(688,60000000,4770000,1440000,19600,290,0,3000000) #欧洛巴士
    global_MonsterBaseList[688].dex=1002
    postset(687,80000000,5750000,2750000,3000,250) #鲭海巨妖
    postset(686,40000000,4280000,2650000,100,140) #岱舆长右巨兽
    postset(685,28000000,4660000,1770000,400,138) #岱舆长右勇士
    postset(684,17500000,3730000,2330000,500,144) #岱舆长右
    postset(683,48000000,9500000,4800000,6000,200) #冶鸟形鸠
    postset(682,24000000,3500000,2750000,3200,190) #虺毒妖王
    global_MonsterBaseList[681].name="旱魃之颅:1-0-200:4-3000:4-100"
    postset(681,22000000,5000000,3000000,5000,210) #旱魃之颅
    postset(680,33000000,4150000,2700000,5600,180) #砂毒暴君
    postset(679,25000000,4500000,2800000,4400,200) #螣蛇幼仔
    postset(678,20000000,3300000,2200000,2700,220) #苍玄战甲
    postset(677,24000000,4200000,2400000,5500,190) #天人侍卫
    postset(676,21000000,3800000,2700000,3000,200) #驭兽童
    postset(675,50000000,3750000,2500000,4500,125) #荆棘妖灵
    postset(674,12500000,3800000,1600000,5800,200) #下级破军道兵
    postset(673,10000000,3000000,2000000,5000,150) #流动的遗骸
    postset(672,18000000,2920000,1700000,4800,185) #狂暴盘瓠幼仔
    postset(671,25000000,4500000,2000000,6500,210) #无面尸圣
    postset(670,25000000,2750000,2250000,3000,210) #无面尸仙
    global_MonsterBaseList[669].dex=1002
    postset(669,64000000,6750000,3000000,7200,220,0,2000000) #安德雷安
    postset(668,15000000,2850000,1650000,4500,175) #辟空武魂
    postset(667,18000000,3200000,1750000,6000,200) #古代天魔
    postset(666,16000000,2500000,1800000,3600,200) #黄泉幽鬼
    postset(665,20000000,2800000,1200000,4000,190) #蟠龙幼仔
    postset(664,15000000,3600000,2000000,5500,200) #罗刹凰儡
    postset(663,15000000,3600000,2000000,5500,200) #瑶光凰儡
    postset(662,12000000,2700000,1500000,4800,180) #下级贪狼道兵
    postset(661,14000000,2320000,1350000,4500,175) #盘瓠幼仔
    postset(660,11000000,1850000,1400000,2500,190) #下级天策道兵
    postset(659,8500000,1950000,1500000,2100,180) #赤龙战甲
    postset(658,12000000,2250000,1450000,4000,200) #下级羽灵道兵

    global_MonsterBaseList[656].dex=1003
    postset(656,280000000,18500000,10500000,9000,220,50000,1000000) #训仙鸿
    global_MonsterBaseList[655].name="？？？:500000:5-4000000:10-1500-12000000-20000000"
    postset(655,30000000,2800000,1400000,5000,150) #BOSS样例
    postset(654,15000000,2100000,1400000,3800,170) #骑士BOSS
    postset(653,15000000,1750000,1200000,4800,135) #教尊BOSS
    postset(651,10000000,1600000,1150000,2500,140) #战士BOSS分身
    postset(650,15000000,1850000,1250000,3500,140) #战士BOSS
    postset(649,15000000,0,1250000,2000,130) #咏唱者BOSS
    postset(648,7777777,1580000,1180000,3000,140) #奥术法影全家老小
    postset(647,12000000,1800000,1250000,4500,135) #领唱者
    postset(646,9500000,1500000,1100000,2750,135) #执行者
    postset(645,6000000,1600000,1200000,2500,125) #血色牧羊人
    postset(644,10000000,1650000,1150000,1000,120) #假面护教者
    postset(643,8000000,1850000,1000000,1200,140) #成年龙蝠
    postset(642,10000000,1600000,1080000,3500,135) #方界的仆从
    postset(641,15000000,1850000,1250000,2800,150) #解答者
    postset(640,12000000,0,1100000,1800,130) #海尔奥芬特
    global_MonsterBaseList[640].name="海尔奥芬特:300000:2400000-4:5-5-1:15-12000000-240"
    postset(639,9000000,1500000,1100000,3200,120) #忠诚信使
    postset(638,500000,1200000,1300000,2000,1000) #遗忘的巨石
    postset(637,9000000,1100000,850000,1600,125) #冰棘之王
    postset(636,11000000,1400000,800000,2100,130) #洞穴之王
    postset(635,8400000,1350000,800000,1600,130) #遗忘的修罗
    postset(634,8000000,1000000,650000,2500,135) #圣所司事
    postset(633,7000000,1200000,750000,3000,140) #萨卡兰姆
    postset(632,10000000,1150000,800000,1800,150) #遗忘的壁垒
    postset(631,12000000,1700000,1200000,3500,135) #遗忘的领唱者
    postset(630,6500000,1450000,950000,2000,100) #方界超兽
    postset(629,10000000,1500000,500000,2500,100) #节点4
    postset(628,3000000,1800000,800000,3500,100) #节点3
    postset(627,4000000,1000000,600000,900,100) #方界兽
    postset(626,7200000,1250000,750000,1750,135) #灰烬行刑者
    postset(625,9000000,1350000,800000,2000,120) #枢机战争主教
    postset(624,50000000,0,0,1000,0) #节点2
    postset(623,7000000,950000,600000,2700,130) #方界纵横战团
    global_MonsterBaseList[623].name="方界纵横战团:6-40-800:1-3-99&1:6-800&2:2-20"
    postset(622,8000000,1000000,650000,3600,140) #方界战皇
    postset(621,100,2000000,0,10000,0) #节点1
    postset(620,12000000,1100000,720000,2500,130) #狂信者骑士长
    postset(619,7500000,800000,700000,1800,125) #圣光女祭司
    postset(618,7000000,1080000,700000,2000,130) #圣光位面主教
    postset(617,6400000,1050000,600000,1500,125) #方界无影修罗
    postset(616,6500000,960000,580000,2400,120) #方界射影战团
    postset(615,8000000,850000,700000,1200,140) #方界浑金壁垒
    postset(614,7200000,850000,650000,1000,120) #方界守御战团
    postset(613,6000000,720000,400000,2000,130) #方界传奇术士
    postset(612,5500000,650000,400000,1600,120) #方界术法战团
    postset(611,4000000,800000,500000,2500,135) #方界传奇剑圣
    postset(610,5000000,750000,450000,2100,120) #方界猛袭战团

    postset(608,700000,90000,65000,800,100) #白垓
    postset(607,500000,75000,45000,400,100) #白垓
    postset(606,320000,40000,40000,750,85) #星盗法王
    postset(605,380000,56000,40000,750,77) #星盗暴君
    postset(604,280000,55000,33000,1000,80) #星盗芈影
    postset(603,300000,0,20000,300,300) #星空变异物质
    postset(602,300000,0,20000,300,300) #星空古物质
    postset(601,330000,54000,36000,800,75) #星空古生物
    postset(600,210000,60000,32000,1350,82) #波粒羽翼
    postset(599,250000,51000,30000,1200,72) #星炼妖魅
    postset(598,125000,42000,27000,900,70) #虚化辐射尘
    postset(597,320000,39000,30000,750,77) #星盗暴徒
    postset(596,270000,27000,20000,200,100) #铁龙星盗
    postset(595,100000,22500,22500,100,500) #巨型陨石
    postset(594,400000,0,30000,100,70) #星界崇高之力
    postset(593,250000,0,25000,100,70) #星界反射镜力
    postset(592,130000,30000,0,300,78) #星盗
    postset(591,180000,0,25000,500,90) #寅圣星炼师
    postset(590,190000,38000,25000,400,85) #天位星炼师
    postset(589,250000,35000,24000,1600,80) #尘照之触
    postset(588,200000,33000,12000,2500,120) #宇宙引力产物
    postset(587,500000,50000,12000,800,75) #宇宙辐照产物
    postset(586,110000,28000,22000,680,87) #星炼吞噬者
    postset(585,90000,40000,15000,900,82) #星河恐惧
    postset(584,110000,30000,20000,700,80) #星空浮游
    postset(583,180000,45000,28000,550,88) #目力法影

    postset(582,5000000,750000,0,2500,100) #code-根除者X4
    postset(581,2400000,510000,200000,1800,88) #code-幽灵
    postset(580,4000000,350000,280000,400,80) #code-收割者
    postset(579,3600000,580000,240000,3600,77) #code-狂热者
    postset(578,4250000,450000,250000,1000,120,5000,1000000) #XC之皇
    postset(577,3500000,400000,300000,2500,75) #冰冻XC
    postset(576,2500000,999999,0,800,75) #吸血XC
    postset(575,3200000,0,150000,1600,85) #剧毒XC
    postset(574,3000000,500000,250000,400,90) #沟壑XC
    postset(573,5000000,380000,200000,200,80) #禁魔XC
    postset(572,2800000,350000,250000,900,100) #阿凡达XC
    postset(571,1500000,360000,240000,200,150) #自爆XC
    postset(570,10000000,480000,150000,200,50) #绿皮XC
    postset(569,2000000,400000,100000,200,250) #异化XC生物
    postset(568,6000000,600000,200000,2500,100) #code-根除者
    postset(567,4500000,350000,270000,1600,95) #code-巨擘
    postset(566,4000000,380000,220000,1000,105) #晦暗特种师
    postset(565,1500000,320000,320000,1000,100) #返角要塞枢纽
    postset(564,2500000,400000,240000,2000,88) #code-鬼王
    postset(563,3100000,200000,200000,1600,90) #墨芳魅惑
    postset(562,4800000,285000,175000,3200,115) #嘶啸之鳞
    postset(561,1000000,400000,200000,1000,100) #异化传输节点
    postset(560,3000000,250000,250000,1200,70) #code-术士
    postset(559,3800000,300000,170000,4000,90) #code-野狼
    postset(558,3000000,340000,160000,1000,118) #晦暗陆战师团
    postset(557,5000000,320000,150000,1200,98) #异化改造兽人
    postset(556,20000000,1800000,200000,100,300) #异化要塞炮
    postset(555,7200000,500000,300000,4000,110) #圣殿骑士
    postset(554,150000,0,0,0,1000) #嗅探式地雷
    postset(553,6000000,300000,100000,800,85) #异化植物群落
    postset(552,1000000,250000,250000,1000,100) #异化能源枢纽
    postset(551,2400000,275000,175000,1600,100) #骑士王
    postset(550,2000000,220000,160000,900,80) #晦暗法皇
    postset(549,2500000,240000,180000,1500,125) #黑金魔像
    postset(548,2800000,360000,180000,3500,85) #猎鹰
    postset(547,3200000,315000,205000,2800,95) #铁拳
    postset(546,1800000,270000,100000,1800,72) #异化蝙蝠群落
    postset(545,2400000,250000,130000,1200,75) #异化莱姆群落

    postset(544,4500000,240000,150000,1500,120,0,0) #巢祖
    postset(543,3300000,208000,125000,1800,108,0,2000000) #渊皇
    postset(542,2500000,135000,88000,2100,92,0,1000000) #迪皇
    postset(541,7500000,60000,50000,400,0,0,2500000) #迪迪姆
    postset(540,2000000,75000,0,3600,0,100,1000000) #暗渊魔主
    postset(539,300000,70000,30000,400,0) #迪教狂热使徒
    postset(538,500000,60000,60000,100,0) #迪教最终兵器
    postset(536,300000,60000,35000,400,0) #暗渊近卫
    postset(535,100000,0,35000,100,0) #强葬髅
    postset(534,130000,55000,36000,100,0) #魔巢贵族
    postset(533,200000,50000,30000,100,0) #炎龙魔兽
    postset(532,150000,35000,25000,6400,0) #血影魔兽
    postset(531,250000,90000,30000,100,0) #黑剑魔主
    postset(530,160000,25000,30000,100,0) #魔巢黑巫王
    postset(529,90000,40000,28000,100,0) #魔巢黑骑王
    postset(528,100000,32000,25000,100,0) #魔巢守护者
    postset(527,60000,35000,15000,2500,0) #迪教剑圣
    postset(526,120000,28000,18000,100,0) #XC老祖
    postset(525,100000,50000,10000,100,0) #葬髅
    postset(524,40000,22000,12500,900,0) #异化体蝙蝠
    postset(523,80000,25000,15000,100,0) #迪迪姆
    postset(522,120000,0,12000,400,0) #魔巢双子
    postset(521,100000,18000,12500,400,0) #魔巢双子
    postset(519,60000,14000,16000,100,0) #上级甲儡
    postset(518,42000,13500,8000,200,0) #上级魔巢骑兵
    postset(517,15000,17000,11000,200,0) #阴影魔王
    postset(516,40000,7500,10800,100,0) #迪教圣徒
    postset(515,40000,11500,9000,400,0) #上级魔巢护卫
    postset(514,25000,15000,6000,400,0) #强冥髅
    postset(513,35000,11500,8500,100,0) #强冥髅
    postset(512,28000,9000,5500,1600,0) #迪教剑王
    postset(511,32000,7500,5000,100,0) #XC督军
    postset(510,18500,5500,5800,100,0) #法髅
    postset(509,11500,7800,3500,200,0) #苍白蝙蝠
    postset(508,200,3500,5000,100,0) #硬墙
    postset(507,25000,9000,3000,100,0) #黑剑魔主
    postset(506,33000,7700,1700,100,0) #苍白迪姆
    postset(505,15000,6400,3300,100,0) #中级魔巢护卫
    postset(504,9500,5400,2800,200,0) #中级魔巢骑兵
    postset(503,11800,3500,3500,100,0) #迪教使徒
    postset(502,5500,4800,2200,200,0) #阴影迪魔
    postset(501,7000,4500,2000,100,0) #XC勇士
    postset(500,5400,3400,2000,100,0) #冥髅
    postset(499,8000,2400,2500,100,0) #中级甲儡
    postset(498,9000,3200,1500,100,0) #下级魔巢护卫
    postset(497,7200,2100,1280,400,0) #迪教游侠
    postset(496,6000,1800,1000,900,0) #超体蝙蝠
    postset(495,8000,2000,1250,100,0) #迪迪姆
    postset(494,12000,1500,800,100,0) #迪迪姆
    postset(492,3800,1450,550,220,0) #下级魔巢骑兵
    postset(491,200,850,900,100,0) #墙
    postset(490,4800,1350,400,100,0) #血髅

    postset(474,2700000,148000,115000,2200,100,10000,10000000) #普拉斯多
    postset(473,1750000,115000,85000,950,90) #天辉金甲营
    postset(472,1380000,106000,70000,750,66) #天辉神射营
    postset(470,750000,92000,78000,250,95) #天辉铁卫营
    postset(469,950000,100000,75000,750,82) #天辉骁骑营
    postset(468,1100000,90000,90000,500,85) #天辉守御大队
    postset(467,720000,80000,70000,400,75) #天辉奥术大队
    postset(466,950000,100000,65000,900,80) #天辉强袭大队
    postset(454,2000000,100000,90000,1200,90,20000,2000000) #玛朵妮丝
    global_MonsterBaseList[454].name="玛朵妮丝:300000&3:45000:300-8000&1:12-500-400000-3&2:125000-50"
    postset(453,350000,85000,65000,900,67) #影夜龙人长老
    postset(452,1200000,115000,82000,2000,82) #法力湮灭者
    postset(451,600000,95000,65000,900,72) #收割盔甲
    postset(450,800000,108000,80000,1750,75) #冰结之瞳
    postset(449,960000,110000,72000,1600,80) #迷幻噩梦
    postset(448,780000,102000,60000,780,73) #影夜龙将
    postset(447,820000,98000,70000,2500,68) #续驰暝瑚
    postset(446,450000,105000,68000,850,62) #奥术之影
    postset(445,700000,96000,65000,900,66) #星魂兽人
    postset(444,640000,85000,65000,650,63) #阴影侍从
    postset(443,530000,115000,48000,1200,60) #诅咒翼兽
    postset(442,480000,99000,54000,1460,60) #不朽死者
    postset(441,510000,81000,63000,800,63) #贝基拉玛修

    postset(440,1500000,98000,50000,1600,75) #突风夜魇战兵
    postset(439,600000,95000,65000,900,72) #收割盔甲
    postset(438,800000,70000,70000,750,78) #夜魇甲兵
    postset(437,380000,90000,68000,1300,70) #厄运骑士
    postset(436,550000,72000,60000,1150,65) #狂怒兽战士
    postset(435,500000,80000,64000,1300,64) #遗忘骑士
    postset(434,320000,80000,45000,2200,58) #血腥翼兽
    postset(433,370000,70000,55000,1850,63) #丛林幽影
    postset(432,720000,80000,40000,900,80) #黄金骁骑
    postset(431,500000,75000,45000,750,60) #水之骁骑
    postset(430,500000,75000,45000,750,60) #火之骁骑
    postset(429,450000,90000,50000,1035,60) #精锐戮尽骑士
    postset(428,500000,30000,50000,400,50) #封尘魔导师
    postset(427,300000,30000,50000,400,50) #封尘魔导师
    postset(426,2500000,125000,40000,100,50) #灾厄之瞳
    postset(425,350000,70000,40000,400,50) #恐怖果实
    postset(424,300000,60000,40000,400,50) #恐怖之芽
    postset(423,250000,50000,40000,400,50) #恐怖之种
    postset(422,500000,100000,35000,100,50) #恶魔果实
    postset(421,400000,80000,32500,100,50) #恶魔之芽
    postset(420,350000,70000,30000,100,50) #恶魔之种
    postset(419,1111111,0,33333,1111,77) #三途川之影
    postset(417,460000,55000,40000,400,56) #妖精魔导师
    postset(416,350000,64000,38000,900,53) #妖精风行者
    postset(415,240000,51000,32000,1280,47) #妖精斥候
    postset(413,1180000,95000,56000,900,75,5000,1000000) #风凌影
    global_MonsterBaseList[413].dex=1000
    postset(412,1020000,90000,58000,1360,62,3000,800000) #卡罗尔
    postset(411,950000,65000,45000,400,65,3000,800000) #阿克苏卡恩
    postset(410,150000,41000,28000,250,50) #瘟疫死者
    postset(409,650000,55555,22222,350,70) #地狱火
    postset(404,200000,40000,40000,200,60) #冰封夜魇甲兵
    postset(403,180000,44000,33000,300,48) #冰封夜魇法兵
    postset(402,175000,50000,30000,500,53) #冰封夜魇战兵
    postset(401,450000,90000,50000,950,60) #精锐戮尽骑士
    postset(400,560000,72000,48000,640,57) #鲁姆斯克巫妖
    postset(399,210000,60000,20000,750,44) #龙蝠幼仔
    postset(398,480000,70000,45000,600,54) #魂渊战驹
    postset(397,40000,55555,44444,100,800) #异界狱石
    postset(396,280000,42000,36000,300,50) #秘湮术士
    postset(395,320000,52500,35000,550,66) #黑骑士
    postset(394,444444,0,33333,888,77) #三途川之影
    postset(393,240000,48000,25000,1600,56) #奥斯塔里剑狂
    postset(392,300000,40000,27500,520,61) #红雾军团先锋
    postset(391,220000,35000,25000,400,48) #荒邪猎魂者
    postset(390,220000,38500,27800,300,72) #艾兹尤格战士
    postset(389,125000,95000,48000,2500,50,3000,800000) #西诺比
    postset(388,1280000,88000,60000,1180,75,3000,800000) #梦多古
    postset(387,1440000,98000,62000,1000,70,4000,1000000) #训仙宇
    global_MonsterBaseList[387].name="训仙宇:8-500:1-8000-10&1003:45-55:10-20-500&1002"
    global_MonsterBaseList[387].dex=1000
    postset(386,480000,62000,36000,1050,42) #嗜血剥皮斥候
    postset(385,480000,66000,40000,650,55) #天辉战团统军
    postset(375,180000,27000,25000,200,60) #精锐天辉甲兵
    postset(374,130000,25000,18000,400,40) #精锐天辉法兵
    postset(373,100000,34000,17000,800,45) #精锐天辉战兵
    postset(367,500000,78000,55000,750,65) #上级圣堂骑士
    postset(366,400000,66000,50000,330,54) #蓝心冰川法师
    global_MonsterBaseList[366].name="蓝心冰川法师:8000:3-10000:8-250-50000-2:5-5-300-50"
    postset(365,600000,68000,48000,250,75) #荆棘王庭近卫
    postset(364,420000,75000,38000,480,55) #星隐游侠
    postset(363,250000,60000,35000,200,120) #诺伦铁壁卫士
    postset(362,320000,54000,40000,450,50) #幻寂大魔导师
    postset(361,360000,48000,35000,750,64) #圣堂骁骑
    postset(360,440000,53500,37800,460,56) #厄西埃勇士
    global_MonsterBaseList[360].magicresist=-33
    postset(359,210000,44000,36500,600,72) #卫火盟弟子
    postset(358,240000,48000,25000,1600,56) #坎冬尼斯剑皇
    postset(357,260000,33000,29000,220,44) #遮面咒术师
    postset(356,350000,37000,28700,370,53) #高阶守夜骑士
    #  postset(333,666666666,66666666,66666666,6666,666) #无敌阻激
    postset(355,233000,43800,29000,560,38) #希尔芙猎杀者
    postset(354,300000,0,30000,700,45) #狂暴猛毒翼蛇
    postset(353,333333,33333,33333,333,33) #风之精灵
    postset(352,588000,94000,62000,1080,48) #中级风之祭司
    postset(351,188000,39600,29700,700,46) #希尔芙铁弩手
    postset(350,260000,27400,20200,400,47) #圣光术士
    postset(349,150000,30000,20000,100,85) #光魔导战甲
    postset(348,300000,40000,25000,500,64) #绝对正义神甫
    global_MonsterBaseList[348].name="绝对正义神甫:349-9:25000-25000:5:5-10&1"
    postset(347,350000,38500,28500,500,70) #圣魂战兵
    postset(346,999999,40000,20000,400,40) #颤栗的凶残
    postset(345,180000,31000,24000,450,60) #沙浪骑将
    postset(344,465000,48000,30000,560,67) #训雷
    postset(343,176000,38500,25000,760,45) #暴风之翼莱娅
    global_MonsterBaseList[343].name="暴风之翼莱娅:90:25000-300:12000-240"
    postset(342,174000,27700,17700,400,36) #漂泊死者
    postset(341,58000,23300,17700,300,30) #流浪死者
    postset(340,85000000000,4250000000,2750000000,22800,342,300000,58000000) #克里瑟历斯
    global_MonsterBaseList[340].dex=1004
    global_MonsterBaseList[340].name="克里瑟历斯:5-35000000000:3000000000-30-12000:2-10-25000-17500000000-10"
    postset(339,180000,27000,20700,880,43) #碧蓝羽翼
    postset(338,210000,33800,26800,600,44) #风神翼蛇
    postset(337,440000,25500,24000,340,40) #巨型沙鹫
    postset(334,96000,27600,18400,450,38) #飓风哈比术士
    postset(333,75000,25000,19200,500,35) #飓风沙漠哈比
    postset(332,68000,23800,17600,420,31) #沙漠哈比
    postset(331,245000,27700,21000,380,46) #皇家英雄法师
    postset(330,240000,36000,24000,880,50) #暮影剑圣
    postset(329,215000,32500,23000,380,58) #皇家英雄骑士
    postset(328,330000,28500,22700,750,52) #沙暴恶灵
    postset(327,145000,26500,20800,520,46) #地狱吟游者
    postset(326,280000,20000,10000,300,40) #死之漂泊者
    postset(325,132000,28000,19000,450,30) #饥渴死者
    postset(324,400000,25000,0,300,0) #诅咒玛荷坎王
    postset(323,250000,28200,24600,270,40) #玛荷坎伊斯托
    postset(322,180000,24800,22400,230,37) #玛荷坎伊姆
    postset(321,198000,44000,27500,480,58) #成体夜魇战兵
    postset(320,240000,27500,20000,250,45) #绿洲君王
    postset(319,125000,25000,18500,385,34) #溺毙死者
    postset(318,145000,36000,24500,500,54) #希尔芙沙剑士
    postset(317,196000,28800,21800,350,50) #希尔芙沙斗士
    postset(316,198000,36500,26800,640,42) #风之祭司
    postset(315,160000,25300,23500,250,45) #希尔芙风术士
    postset(314,172000,34800,24500,480,35) #希尔芙暗杀者
    postset(313,85000,21250,18750,180,30) #绿洲侦察者
    postset(312,128000,25600,20500,170,43) #绿洲征战者
    postset(311,118000,24200,16500,210,37) #绿洲袭击者
    postset(310,135000,24500,19500,330,48) #沙浪骑兵
    postset(309,130000,22500,16800,180,35) #大玛荷坎达
    postset(308,280000,23200,18200,420,33) #砂魔法影
    postset(306,128000,23500,17500,400,42) #沙地小恶魔
    postset(305,108000,22400,17800,200,36) #绿洲掠夺者
    postset(304,50000,25000,10000,100,0) #失落的灵魂
    postset(303,72000,22800,16000,540,27) #沙漠之翼
    postset(302,120000,24500,13500,325,29) #干燥死者
    postset(301,96000,21000,18000,160,32) #玛荷坎达
    postset(300,11800,1950,1420,220,7) #教团苦修者
    postset(298,160000,18200,14500,250,24) #暗影安波拉
    postset(299,100000,32000,20800,348,45) #暗影大长老
    postset(297,185000,27500,19800,330,42) #暗影长老
    postset(296,118000,18000,15800,340,37) #暗影格兰特
    postset(295,450000,19800,11800,500,35) #无影的炼
    global_MonsterBaseList[295].dex=1000
    postset(294,320000,20000,12500,450,40) #嘲弄的索米尔
    postset(293,345000,25600,13800,500,35) #奇袭的玛科斯
    postset(292,180000,22500,12500,900,-10) #暗影赛特
    global_MonsterBaseList[292].magicresist=-10
    postset(291,450000,21000,12000,1600,-25) #狂战的巴斯卡
    global_MonsterBaseList[291].magicresist=-25
    postset(290,80000,15000,12500,320,35) #祭坛督军
    postset(289,8000,9999,9999,100,600) #冰封地狱岩
    postset(288,132000,10600,9200,250,36) #寒冬魔导
    postset(287,71000,13200,9500,480,26) #符文盔甲
    postset(286,165000,17500,15000,300,40) #暗影菲多洛德
    postset(285,152000,19500,14250,450,35) #暗影兰斯
    postset(284,118000,16600,9800,280,28) #暗影加沃雷
    postset(283,98000,17800,10800,320,32) #暗影亚切尔
    postset(282,125000,15000,12000,350,36) #暗影特里斯特
    postset(281,115000,14000,12700,210,33) #精锐贝基拉冈
    postset(280,140000,13200,10400,250,32) #暗影维扎德
    postset(279,135000,13700,12000,240,40) #暗影沃瑞尔
    postset(278,95000,14500,10800,400,28) #暗影莱汀
    postset(277,580000,72767,44598,740,50) #拉格纳斯
    postset(275,280000,16500,12800,300,18) #寒冬骨龙
    postset(274,380000,32000,25000,440,45) #高阶祭坛督军
    postset(273,80000,15000,12500,320,35) #祭坛督军
    postset(272,8000,9999,9999,100,600) #冰封地狱岩
    postset(271,132000,10600,9200,250,36) #寒冬魔导
    postset(270,71000,13200,9500,480,26) #符文盔甲
    postset(269,50000,11500,7000,350,27) #冰封骸骨之王
    postset(268,178000,12100,10200,280,20) #极冰兽王
    postset(267,117000,11700,9800,240,15) #极冰兽人
    postset(266,150000,11000,9200,180,18) #恐怖食人魔
    postset(264,105000,12000,8500,300,28) #地狱诗人
    postset(262,80000,9999,9999,160,60) #冰封甲兵统领
    postset(261,90000,9600,7200,270,15) #冰封法兵统领
    postset(260,50000,10800,6500,300,22) #冰封骸骨督军
    postset(259,50000,9900,5800,210,17) #冰封骸骨
    postset(258,110000,11000,5000,630,25) #砂牙
    postset(257,180000,9500,6500,300,40) #冰封地狱
    postset(256,64000,9800,7800,270,24) #孤高的魔导师
    postset(255,72000,10500,6800,250,22) #冰晶噩梦
    postset(254,38500,11500,6000,280,15) #冰霜翼兽
    postset(253,60000,12000,7200,420,27) #寒冬战兵统领
    postset(252,37500,8500,6500,250,18) #寒冬哨兵
    postset(251,85000,9650,6850,330,40) #雪地魔能傀儡
    postset(248,50000,8888,8888,120,50) #冰封夜魇甲兵
    postset(247,60000,7500,7200,200,15) #冰封夜魇法兵
    postset(246,31000,10800,6800,370,21) #冰封夜魇战兵
    postset(245,48000,9000,5800,260,20) #雪地漫步者
    postset(244,70000,7200,4500,150,14) #冰棘死者
    postset(243,58000,6900,6000,160,24) #贝基拉冈警卫
    postset(242,40000,7600,5500,230,17) #雪地爬行者
    postset(241,256000,13800,7800,280,33) #提里奥斯
    postset(240,62000,6400,4300,120,21) #涅尔玟
    postset(237,70000,722,456,140) #爱丽丝
    postset(236,63000,9000,6000,300,20) #死亡人形
    postset(235,44000,8800,6400,300,20) #绝望人形
    postset(234,37500,7800,5800,300,20) #背叛人形
    postset(233,50000,9500,4500,320,28) #鬼影突骑
    postset(232,30000,6000,6000,250,35) #狱炎魔导师
    postset(231,45000,6800,5800,400,15) #幽亡法影
    postset(230,8000,6000,8000,100,20) #幽灵夜魇战兵
    postset(229,38000,7400,5900,350,24) #剧毒守卫
    postset(228,50000,6350,3650,130,0) #怨恨的人偶
    postset(227,32000,7200,5200,380,14) #猎杀之影
    postset(226,21000,6600,5500,450,22) #符文盔甲
    postset(225,38000,6200,4800,150,18) #狱炎魔导师
    postset(224,9000,7900,5600,360,120) #阵亡形态
    postset(223,35000,5200,5000,100,11) #银杖
    postset(222,42000,5850,4500,140,19) #贝基拉冈
    postset(216,25000,4500,3500,400,25) #恶魔骑士梅罗
    postset(215,50000,7000,5000,100,22) #暗影破法者
    postset(214,26000,6500,4800,100,21) #破法者
    postset(213,15000,5500,5000,150,23) #暗影之核
    postset(212,25000,4500,3500,125,25) #圣骑士梅罗
    postset(211,32500,3720,3080,160,10) #精锐贝基拉玛
    postset(210,13000,4200,3700,360,8) #攻坚之影
    postset(209,12500,4800,2200,250,7) #暗影翼兽
    postset(208,10000,0,2800,900,6) #冰凛法影
    postset(207,6000,3000,4000,100,500) #狱岩傀儡
    postset(204,25000,3380,2500,320,9) #巴拉那战将
    postset(203,12800,4100,2700,200,18) #下级圣堂武士
    postset(202,19000,4000,3000,140,14) #遗忘的雕像
    postset(201,9000,6000,8000,150,20) #圣洁夜魇战兵
    postset(200,30000,4400,2700,280,11) #影夜龙人
    postset(199,24400,4750,3750,300,27) #腐化圣堂武士
    postset(197,14000,3950,3750,270,8) #痛苦石像鬼
    postset(196,22000,3800,3200,270,8) #暗夜石像鬼
    postset(195,12800,3430,2650,280,0) #燃烧小恶魔
    postset(194,40000,3500,2500,100,12) #涅尔玟分身
    postset(193,5000,3100,2100,500,6) #燃火法影
    postset(192,46000,4500,3200,100,15) #涅尔玟
    postset(191,17500,2920,2660,200,3) #熔岩兽人
    postset(189,3900,4200,2100,250,5) #燃烧地狱蝠
    postset(188,8800,3350,1750,330,12) #迷失的剑士
    postset(47,340515,11500,6800,300,65) #地狱火
    postset(99,4200,1450,920,400) #沙岚武尊
    postset(116,5600,1042,773,180) #圣殿骑士
    postset(117,7500,1025,725,200) #玛荷托拉族皇
    postset(128,4500,1150,780,320) #中空盔甲
    postset(129,2400,1055,872,280) #厄运骑士
    postset(130,3333,1111,888,500) #恐怖之芽
    postset(131,2000,1080,1050,100) #隔断之瞳
    postset(132,5000,1337,862,240) #龙人
    postset(135,3773,1275,1020,270) #古代护陵
    postset(136,4500,1380,1150,310) #古代护陵将军
    postset(137,9000,1368,992,270) #玛荷托拉族皇
    postset(138,6400,1377,1087,50) #古代食人魔
    postset(139,3000,1288,878,900) #修罗幻影
    postset(140,5300,1403,1035,260) #恶魔侵蚀者
    postset(141,6800,1350,1125,175) #魔化卡巴内
    postset(142,22000,1500,800,300) #斯多姆狂战士
    postset(143,3000,1333,1333,400) #倒影之瞳
    postset(145,4000,1444,1444,444) #真倒影之瞳
    postset(146,18000,1400,1350,370) #恐怖利刃
    postset(159,580000,72767,44598,740,50) #
    postset(160,2460000,185000,106000,1750,90) #暗影王者
    postset(169,7800,1650,1650,130) #贝基拉玛
    postset(170,3600,1990,1550,240) #地狱蝠
    postset(171,5000,1720,1640,220) #埋葬的卒子
    postset(172,9000,1900,1720,160) #贝基拉玛警卫
    postset(173,8000,1490,1760,100) #灼热术士
    postset(174,7900,2100,1650,260) #小恶魔
    postset(175,4000,2250,1380,400) #厄运剑髅
    postset(176,5000,2300,1580,320) #厄运剑铠
    postset(177,6000,2350,1780,240) #厄运剑宗
    postset(178,3700,1620,1370,180) #巴拉那侦察者
    postset(179,75000,3030,2280,300,10) #乌诺巨人
    postset(180,6000,1900,1900,100,300) #狱岩傀儡
    postset(181,16000,2180,1720,160) #地狱食人魔
    postset(182,12000,2360,1600,130) #食人魔法师
    postset(184,8888,2880,2280,150,5) #波动的火焰
    postset(186,13500,2720,2450,200,4) #精锐贝基拉玛
    postset(187,35000,3500,3500,270,8) #黑曜石像鬼
    global_MonsterBaseList[133].name="魔导师遗骸:10:360:300-200&3:720-3&1:30-50&2"


    playerlevel=16

    l=_clip(playerlevel,min_=16.5)
    a=4.5+(l-15)*3
    b=217
    global_MonsterBaseList[b].level.ResetValue( int(l) )
    postset(b,(3200*a),(850*a),(550*a),180,5+(2*a)) 
    b=218
    global_MonsterBaseList[b].name="绝不信任:"+   str(int(a*150))
    global_MonsterBaseList[b].level.ResetValue( int(l) )
    postset(b,(2750*a),(900*a),(380*a),900,3+(1.6*a)) 
    b=219
    global_MonsterBaseList[b].level.ResetValue( int(l) )
    postset(b,(1800*a),(750*a),(0*a),100+(8*a),5+(4*a))
    b=220
    global_MonsterBaseList[b].name="永无宁静:"+  str(int(a*90))
    global_MonsterBaseList[b].level.ResetValue( int(l) )
    postset(b,(5500*a),(0*a),(600*a),120,4+(1.8*a)) 
    b=221
    global_MonsterBaseList[b].name="疯狂索取:15-2.5-"+str(int(a*2))+":"+str(int(a*3))
    global_MonsterBaseList[b].level.ResetValue( int(l) )
    postset(b,(3500*a),(880*a),(510*a),240,10+(1*a)) 
    b=238
    global_MonsterBaseList[b].name="尽数掠夺:"+str(int(a*50))+":10:2"
    global_MonsterBaseList[b].level.ResetValue( int(l) )
    postset(b,(3000*a),(950*a),(720*a),130,12+(2*a))
    b=239
    global_MonsterBaseList[b].level.ResetValue( int(l) )
    postset(b,(4800*a),(1020*a),(680*a),500,11+(3*a)) 






    postset(464,600000,95000,65000,900,72) #收割盔甲
    postset(463,1200000,115000,82000,2000,82) #法力湮灭者
    postset(462,780000,120000,60000,580,73) #影夜龙将
    postset(461,820000,98000,70000,2500,68) #续驰暝瑚
    postset(460,450000,105000,68000,850,62) #奥术之影
    postset(459,700000,96000,65000,900,66) #星魂兽人
    postset(458,640000,85000,65000,650,63) #阴影侍从
    postset(457,530000,115000,48000,1200,60) #诅咒翼兽
    postset(456,480000,99000,54000,1460,60) #不朽死者
    postset(455,510000,81000,63000,800,63) #贝基拉玛修
    postset(465,1720000,118000,75000,1280,85) #汪迪兰特

    global_MonsterBaseList[343].health.ResetValue(176000)
    global_MonsterBaseList[344].health.ResetValue(465000)
    global_MonsterBaseList[344].attack.ResetValue(48000)
    global_MonsterBaseList[344].defence.ResetValue(30000)
    for actorbase in global_MonsterBaseList:
        actorbase.deal_skillList()






# 全局事件总线（注册/取消/触发）
class GlobalItemList(list):
    def showitems(self,maxnumber=10):
        for item in self[:maxnumber]:
            print(item.name)

#custom dictionary class
class EventListenerDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, [])
        self[key].append(value)
class GlobalEventBus:
    def __init__(self):
        self.listeners = EventListenerDict()
global_event_listeners =  EventListenerDict()

def add_listener(event_name,   listener):#**kwargs_listener):
    """注册事件监听器：add_listener('OnEffectStart', handler)"""
    global_event_listeners.setdefault(event_name, []).append(listener)


def remove_all_related_listeners(listener):
    """取消注册事件监听器"""
    for event_name in list(global_event_listeners.keys()): 
        if listener in global_event_listeners[event_name]:
            global_event_listeners[event_name].remove(listener)


def dispatch_event(event_name, **kwargs):#"OnAttack"
    """创建 Event 并调用所有监听器（异常会被捕获并打印）"""
    ev = Event(name=event_name, **kwargs)
    for listener in list(global_event_listeners.get(event_name, [])):
        # check conditions in listener.condition_kwargs
        conditions_met = True
        if listener.condition_kwargs:
            for key, value in listener.condition_kwargs.items():
                if ev.kwargs.get(key) != value:#条件判断
                    conditions_met = False
                    break
        if conditions_met:
            # listener.kwargs  updated with ev.kwargs if type==EvtKwarg
            updated_kwargs = listener.kwargs.copy()
            for k, v in listener.kwargs.items():
                if isinstance(v, EvtKwarg):
                    updated_kwargs[k] = ev.kwargs.get(v.keyname)
            listener.callback(**updated_kwargs)

# add_listener("OnEffectStart", on_effect_start_burn)
def event_record_damage(amount, source, target, damagetype, state):
    """发布伤害事件（封装现有调用点）"""
    dispatch_event("OnRecordDamage", amount=amount, source=source, target=target, damagetype=damagetype, state=state)

def event_oneffectstart(caster, target, effect):
    """发布效果开始事件：监听器接收参数 (caster, target, effect) 在 ev.kwargs 中。"""
    dispatch_event("OnEffectStart", caster=caster, target=target, effect=effect)
def event_oneffectend(caster, target, effect):
    """发布效果结束事件：监听器接收参数 (caster, target, effect) 在 ev.kwargs 中。"""
    dispatch_event("OnEffectEnd", caster=caster, target=target, effect=effect)
def event_onturnstart(turn_index): #"OnTurnStart"
    dispatch_event("OnTurnStart", turn_index=turn_index)
def event_onturnend(turn_index): #"OnTurnEnd"
    dispatch_event("OnTurnEnd", turn_index=turn_index)
#battle start
def event_onbattlestart(battle_instance): #"OnBattleStart"
    dispatch_event("OnBattleStart", battle_instance=battle_instance)
#battle end
def event_onbattleend(battle_instance): #"OnBattleEnd"
    dispatch_event("OnBattleEnd", battle_instance=battle_instance)
# actor state change check
def event_onactorstatechange(actor, reason="recheck"):
    dispatch_event("OnActorStateChange", actor=actor, reason=reason)



empty_magic_effect=Effect(name="空效果",magnitude=0,duration=0,archetype=EffectType.Empty)
# empty_magic_effect=Effect("empty_magic_effect")
empty_buff=Effect("empty_buff",magnitude=1,duration=1)

Justin=Actor(name="贾斯汀",health=ActorValue(currentvalue=150,maxvalue=1000),mana=ActorValue(currentvalue=4,maxvalue=100),level=6,attack=75,defence=63,armor=5,atkrate=100,avoid=0,block=0,healthregen=4)

# global_SkillList=[Skill()]
# global_EffectList=[empty_magic_effect]
# global_MonsterBaseList=[copy.deepcopy(Justin)]
global_SkillList=GlobalItemList()
global_EffectList=GlobalItemList()
global_MonsterBaseList=GlobalItemList()
global_SkillList.append(Skill())
global_EffectList.append(empty_magic_effect)
global_MonsterBaseList.append(copy.deepcopy(Justin))
#加载 魔法效果
dat_effect = pandas.read_csv("./csv/Effects.csv",  header=0)
for i in range(len(dat_effect)):
    dic=dat_effect.loc[i].to_dict()

    effectbase=Effect(name=dic["Name"],baseID=dic['BaseID'],magnitude=dic["Magnitude"],
                          archetype= dic['Archetype']  ,keywords_stack=dic["keywords_stack"]
                          ,max_stack=dic["max_stack"],
                      associatedItem= dic['AssociatedItem'] , duration=dic["Duration"],evalfunstr=dic["evalfunstr"] )
    # effectbase=Effect()
    global_EffectList.append(effectbase)

#加载 永不复还 技能
dat_skill = pandas.read_csv("./csv/skills.csv",  header=0)
for i in range(len(dat_skill)):
    dic=dat_skill.loc[i].to_dict()

    skillbase=Skill(name=dic["Name"],baseID=dic['BaseID'],default_param=dic["DefaultParams"]
                    ,mana_cost=dic["mana_cost"],targetpermit= dic['targetpermit']  ,delivery= dic['Delivery']  ,skilltype= dic['SkillType']
                    ,description=dic["Description"],effect_dict=dic["effect_list"] )
    skillbase.process_skill_effects()
    global_SkillList.append(skillbase)
#加载 永不复还 敌人单位
dat = pandas.read_csv("./csv/enemies.csv", comment='%', header=0)
print(len(dat))
for i in range(len(dat)):
    # p
    dic=dat.loc[i].to_dict()
    if dic["MagicDef"]  ==111:
        dic["MagicDef"]=0
    actorbase=Actor(name=dic["Name"],baseID=dic['BaseID'],level=dic["Level"],health=dic["HealthMax"],mana=dic["ManaMax"],attack=dic["Attack"],defence=dic["Defence"],
        atkrate=dic["AtkRate"],armor=dic["Armor"] ,avoid=0,magicblock=0,magicresist= dic["MagicDef"],gold=dic["Gold"],expgain=dic["ExpGain"],
        healthregen=dic["HealthRegen"],manaregen=dic["ManaRegen"],skilllist=loadskill(dic))
    # print(actorbase.name)
    
    
    global_MonsterBaseList.append(actorbase)
    


postset_bat()


if __name__ == "__main__":
    ActorValueType('health')
    print(empty_magic_effect)
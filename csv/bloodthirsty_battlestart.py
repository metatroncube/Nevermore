bloodthirsty_battlestart
OnBattleStart
def bloodthirsty_battlestart(self,custom_param=0,**kwargs):
    self.Recover()
    injured_proportion=1-(self.target.health.currentvalue/self.target.health.maxvalue)
    injured_proportion=self.target.enemy_injured_proportion()
    print("injured_proportion",injured_proportion)
    self.value=self.magnitude*(injured_proportion)*100
    print("atkrate buff",self.value)
    self.Enforce()
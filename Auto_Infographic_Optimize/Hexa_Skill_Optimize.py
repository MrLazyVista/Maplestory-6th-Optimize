from PIL import Image, ImageDraw, ImageFont
import os
import numpy

## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
# Fragment based optimization FragBase = True
# Energy based optimization FragBase = False
# Optimize for rerolling Hexa Core = True
FragBase    = True
Hexa_Stat_Include = True
Hexa_Maxed  = False
# Use decimal values 98% = 0.98, 612% = 6.12, etc etc
# Damage is Boss% + Damage%,
# IED is what you see on character sheet
# Hidden IED is IED that doesnt show up on your character page, explorer link, built into skills, debuffs, etc etc
Damage      = 7.00
IED         = 0.97
Hidden_IED  = 0.4
Boss_Def    = 3.80

# Before Origin BA values (use fraction values 0.25, 0.5, 0.1, etc etc)
# A_1 represents the BA contribute of your 4th job skill that is boosted
# B_1 means your first 5th job skill (Spear for ex)
# B_2 for the second 5th job skill (Radiant Evil)
# B_3 for third (Cyclone), etc etc
# C_1 represents your Origin Skill, and how big you expect it to be (BA percentage wise)
# Input an estimated BA contribution for level one if Origin is currently nonexistant
A_1     = 0.25
B_1     = 0.25
B_2     = 0.20
B_3     = 0.15
B_4     = 0.08
C_1     = 0.10

# Current Skill Levels (6th Core)
A_1_Current   = 0
B_1_Current   = 0
B_2_Current   = 0
B_3_Current   = 0
B_4_Current   = 0
C_1_Current   = 0

# These stats (Crit_Dmg, Att_Power, Att_Perc, Stat) are only used if Hexa_Stat_Include is True
Crit_Dmg  = 1.48
Att_Power = 8434
Att_Perc  = 1.45
Stat      = 75027
# Hexa_Stat_ Main/Alt values are only used if Hexa_Maxed is True, uses a [level,Stat] format, use the following strings of "Stat"
# 'Crit Damage','Boss Damage','Ignore Def','Reg Damage','Attack','Stat'
Hexa_Stat_Main  = [4 , 'Boss Damage']
Hexa_Stat_Alt_0 = [8 , 'Attack']
Hexa_Stat_Alt_1 = [8 , 'Stat']

## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
## You can ignore everything below here, let the magic machine do its work

# for debugging purposes
def ListPrint(List):
    for i in range(len(List)):
        print(List[i])

# Damage gain vs level
def Fill_Boost(List,ID,Aux,Val,Start,End):
    sig_fig     = 8
    for i in range(Start,End):
        if   ID == "A":
            # should be adjusted to match class specific values (although most are gonna be similiar)
            List[i]     = ((240+5*(i+1))/225 * Aux - 1) * Val
        elif ID == "B":
            if (i+1) < 10:
                List[i] = round((0.11 + i*0.01) * Aux * Val,sig_fig)
            elif (i+1) < 20:
                List[i] = round((0.16 + i*0.01) * Aux * Val,sig_fig)
            elif (i+1) < 30:
                List[i] = round((0.21 + i*0.01) * Aux * Val,sig_fig)
            elif (i+1) == 30:
                List[i]  = round(0.60            * Aux * Val,sig_fig)
        elif ID == "C":
            if i == 0:
                List[i] = C_1
            elif (i+1) < 10:
                CAux     = 1
                List[i] = C_1 + round((i) * Aux * CAux * Val/30,sig_fig)
            elif (i+1) < 20:
                CAux     = (1-Boss_Def*(1-IED)*(1-.2))/(1-Boss_Def*(1-IED))
                List[i] = C_1 + round((i) * Aux * CAux  * Val/30,sig_fig)
            elif (i+1) < 30:
                CAux     = (1-Boss_Def*(1-IED)*(1-.2))/(1-Boss_Def*(1-IED)) * (1 + Damage + .2) / (1 + Damage)
                List[i] = C_1 + round((i) * Aux * CAux  * Val/30,sig_fig)
            elif (i+1) == 30:
                CAux     = (1-Boss_Def*(1-IED)*(1-.2)*(1-0.3))/(1-Boss_Def*(1-IED)) * (1 + Damage + .2 + .3) / (1 + Damage)
                List[i] = C_1 + round((i) * Aux * CAux  * Val/30,sig_fig)
    return List

# Cost to Reach a certain level
def Fill_Costs(List,Start):
    Result_List = Start*[0]
    for i in range(Start,len(List)):
        if i == Start:
            Result_List.append(List[i])
        else:
            Result_List.append(Result_List[-1] + List[i])
    return Result_List

# if a lv 9 is less efficient than a lv 10 then the 9 is removed from the list implying a 8 -> 10 jump
def SequentialFilter(List):
    Exit_List = [List[0]]
    for i in range(1,len(List)):
        if List[i][0] > Exit_List[-1][0]:
            Exit_List.append(List[i])
    return Exit_List

def ListByListDivide(List_Top,List_Bot):
    Exit_List = len(List_Bot) * [0]
    for i in range(len(List_Bot)):
        if List_Bot[i] != 0:
            Exit_List[i] = List_Top[i] / List_Bot[i]
    return Exit_List

def ListSubtractConstant(List,Level):
    Exit_List = []
    if Level == 0:
        Subtract = 0
    else:
        Subtract = List[Level - 1]
        
    for i in range(len(List)):
            Exit_List.append(List[i] - Subtract)
    return Exit_List

def Reverter(Value,Level,List):
    A = 1
    if Level > 0:
        A = 1 + List[Level-1]
    B = Value / A
    C = Value - B
    return B, C

def GiveMeCleanValues(Main,Current,Level,Type):
    Clean_Value = 0
    if Main == True:
        if Type == 'Ignore Def':
            Clean_Value = 1 - ( 1 - Current )/(1-Stat_Values[Type] * Main_Multi[Level])
        else:
            Clean_Value = Current - Stat_Values[Type] * Main_Multi[Level]

    else:
        if Type == 'Ignore Def':
            Clean_Value = 1 - ( 1 - Current )/(1-Stat_Values[Type] * Alt_Multi[Level])
        else:
            Clean_Value = Current - Stat_Values[Type] * Alt_Multi[Level]
    return Clean_Value

if FragBase:
    #Fragment cost stuff
    A_cost =[50
    ,15
    ,18
    ,20
    ,23
    ,25
    ,28
    ,30
    ,33
    ,100
    ,40
    ,45
    ,50
    ,55
    ,60
    ,65
    ,70
    ,75
    ,80
    ,175
    ,85
    ,90
    ,95
    ,100
    ,105
    ,110
    ,115
    ,120
    ,125
    ,250]
    
    B_cost = [75
    ,23
    ,27
    ,30
    ,34
    ,38
    ,42
    ,45
    ,49
    ,150
    ,60
    ,68
    ,75
    ,83
    ,90
    ,98
    ,105
    ,113
    ,120
    ,263
    ,126
    ,135
    ,143
    ,150
    ,158
    ,165
    ,173
    ,180
    ,180
    ,375]
    
    # 0.01 is simply just to avoid a divide by 0 error
    C_cost = [0.01
    ,30
    ,35
    ,40
    ,45
    ,50
    ,55
    ,60
    ,65
    ,200
    ,80
    ,90
    ,100
    ,110
    ,120
    ,130
    ,140
    ,150
    ,160
    ,350
    ,170
    ,180
    ,190
    ,200
    ,210
    ,220
    ,230
    ,240
    ,250
    ,500]
else:
    #Energy cost stuff
    A_cost =[3
    ,1
    ,1
    ,1
    ,1
    ,1
    ,1
    ,2
    ,2
    ,5
    ,2
    ,2
    ,2
    ,2
    ,2
    ,2
    ,2
    ,2
    ,3
    ,8
    ,3
    ,3
    ,3
    ,3
    ,3
    ,3
    ,3
    ,3
    ,4
    ,10]
    
    B_cost = [4
    ,1
    ,1
    ,1
    ,2
    ,2
    ,2
    ,3
    ,3
    ,8
    ,3
    ,3
    ,3
    ,3
    ,3
    ,3
    ,3
    ,3
    ,4
    ,12
    ,4
    ,4
    ,4
    ,4
    ,4
    ,5
    ,5
    ,5
    ,6
    ,15]
    
    # 0.01 is simply just to avoid a divide by 0 error
    C_cost = [0.01
    ,1
    ,1
    ,1
    ,2
    ,2
    ,2
    ,3
    ,3
    ,10
    ,3
    ,3
    ,4
    ,4
    ,4
    ,4
    ,4
    ,4
    ,5
    ,15
    ,5
    ,5
    ,5
    ,5
    ,5
    ,6
    ,6
    ,6
    ,7
    ,20]

A_1_boost   = 30 * [0]
B_1_boost   = 30 * [0]
B_2_boost   = 30 * [0]
B_3_boost   = 30 * [0]
B_4_boost   = 30 * [0]
C_1_boost   = 30 * [0]

Final_List  = []

# Mod Values are the skill BA contributions if there were no 6th progress except for origin(makes the math simplier)
# if C_1_Current = 0 then that means you got a naked skill tree so everything is by default 0
# if C_1 does not equal zero then, some conversions will have to be done
if C_1_Current == 0:
    C_1_Current = 1
    Amod_1  = A_1 / ( 1 + C_1)
    Bmod_1  = B_1 / ( 1 + C_1)
    Bmod_2  = B_2 / ( 1 + C_1)
    Bmod_3  = B_3 / ( 1 + C_1)
    Bmod_4  = B_4 / ( 1 + C_1)
    # in the original script A_1 is for Gungnir(Dark Knight) which has a IED boost component
    # The "Aux" values are multipliers that are meant to compensate for these extra features
    # if there are no auxilary features, just put 1 for the skill
    A_1_Aux         = (1-Boss_Def*(1-IED)*(1-0.4)*(1-.2))/(1-Boss_Def*(1-IED)*(1-0.3)*(1-.2))
    B_1_Aux         = 1
    B_2_Aux         = 1
    B_3_Aux         = 1
    B_4_Aux         = 1
    C_1_Aux         = 1
    A_1_boost = Fill_Boost(A_1_boost,"A",A_1_Aux ,Amod_1 ,0  ,len(A_cost))
    B_1_boost = Fill_Boost(B_1_boost,"B",B_1_Aux ,Bmod_1 ,0  ,len(B_cost))
    B_2_boost = Fill_Boost(B_2_boost,"B",B_2_Aux ,Bmod_2 ,0  ,len(B_cost))
    B_3_boost = Fill_Boost(B_3_boost,"B",B_3_Aux ,Bmod_3 ,0  ,len(B_cost))
    B_4_boost = Fill_Boost(B_4_boost,"B",B_4_Aux ,Bmod_4 ,0  ,len(B_cost))
    C_1_boost = Fill_Boost(C_1_boost,"C",C_1_Aux ,C_1    ,0  ,len(C_cost))
else:
    A_1_Aux         = (1-Boss_Def*(1-IED)*(1-0.4)*(1-.2))/(1-Boss_Def*(1-IED)*(1-0.3)*(1-.2))
    B_1_Aux         = 1
    B_2_Aux         = 1
    B_3_Aux         = 1
    B_4_Aux         = 1
    C_1_Aux         = 1
    A_1_Multi_boost = Fill_Boost(A_1_boost,"A",A_1_Aux ,1 ,0  ,len(A_cost))
    B_1_Multi_boost = Fill_Boost(B_1_boost,"B",B_1_Aux ,1 ,0  ,len(B_cost))
    B_2_Multi_boost = Fill_Boost(B_2_boost,"B",B_2_Aux ,1 ,0  ,len(B_cost))
    B_3_Multi_boost = Fill_Boost(B_3_boost,"B",B_3_Aux ,1 ,0  ,len(B_cost))
    B_4_Multi_boost = Fill_Boost(B_4_boost,"B",B_4_Aux ,1 ,0  ,len(B_cost))
    C_1_Multi_boost = Fill_Boost(C_1_boost,"C",C_1_Aux ,1 ,0  ,len(C_cost))
    Revert_Amod_1,Delta_A_1  = Reverter(A_1,A_1_Current,A_1_Multi_boost)
    Revert_Bmod_1,Delta_B_1  = Reverter(B_1,B_1_Current,B_1_Multi_boost) 
    Revert_Bmod_2,Delta_B_2  = Reverter(B_2,B_2_Current,B_2_Multi_boost)
    Revert_Bmod_3,Delta_B_3  = Reverter(B_3,B_3_Current,B_3_Multi_boost)
    Revert_Bmod_4,Delta_B_4  = Reverter(B_4,B_4_Current,B_4_Multi_boost)
    Revert_C_1   ,Delta_C_1  = Reverter(C_1,C_1_Current,C_1_Multi_boost)
    
    Delta_T = Delta_A_1 + Delta_B_1 + Delta_B_2 + Delta_B_3 + Delta_B_4 + Delta_C_1
    
    Amod_1  = Revert_Amod_1 * ( 1 + Delta_T )
    Bmod_1  = Revert_Bmod_1 * ( 1 + Delta_T )
    Bmod_2  = Revert_Bmod_2 * ( 1 + Delta_T )
    Bmod_3  = Revert_Bmod_3 * ( 1 + Delta_T )
    Bmod_4  = Revert_Bmod_4 * ( 1 + Delta_T )
    C_1     = Revert_C_1 * ( 1 + Delta_T )
    
    A_1_boost = Fill_Boost(A_1_boost,"A",A_1_Aux ,Amod_1 ,0  ,len(A_cost))
    B_1_boost = Fill_Boost(B_1_boost,"B",B_1_Aux ,Bmod_1 ,0  ,len(B_cost))
    B_2_boost = Fill_Boost(B_2_boost,"B",B_2_Aux ,Bmod_2 ,0  ,len(B_cost))
    B_3_boost = Fill_Boost(B_3_boost,"B",B_3_Aux ,Bmod_3 ,0  ,len(B_cost))
    B_4_boost = Fill_Boost(B_4_boost,"B",B_4_Aux ,Bmod_4 ,0  ,len(B_cost))
    C_1_boost = Fill_Boost(C_1_boost,"C",C_1_Aux ,C_1    ,0  ,len(C_cost))

# print(Amod_1,Bmod_1,Bmod_2,Bmod_3,Bmod_4,C_1)

while A_1_Current != 30 or B_1_Current != 30 or B_2_Current != 30 or B_3_Current != 30 or B_4_Current != 30 or C_1_Current != 30:
    A_1_Delta_boost = ListSubtractConstant(A_1_boost,A_1_Current)
    B_1_Delta_boost = ListSubtractConstant(B_1_boost,B_1_Current)
    B_2_Delta_boost = ListSubtractConstant(B_2_boost,B_2_Current)
    B_3_Delta_boost = ListSubtractConstant(B_3_boost,B_3_Current)
    B_4_Delta_boost = ListSubtractConstant(B_4_boost,B_4_Current)
    C_1_Delta_boost = ListSubtractConstant(C_1_boost,C_1_Current)
#    print("Delta_Boost")
#    ListPrint(B_3_Delta_boost)

    A_1_Tcost = Fill_Costs(A_cost,A_1_Current)
    B_1_Tcost = Fill_Costs(B_cost,B_1_Current)
    B_2_Tcost = Fill_Costs(B_cost,B_2_Current)
    B_3_Tcost = Fill_Costs(B_cost,B_3_Current)
    B_4_Tcost = Fill_Costs(B_cost,B_4_Current)
    C_1_Tcost = Fill_Costs(C_cost,C_1_Current)
#    print("TCost")
#    ListPrint(C_1_Tcost)

    # divide FD gain over costs
    A_1_BoostOverCost = ListByListDivide(A_1_Delta_boost, A_1_Tcost)
    B_1_BoostOverCost = ListByListDivide(B_1_Delta_boost, B_1_Tcost)
    B_2_BoostOverCost = ListByListDivide(B_2_Delta_boost, B_2_Tcost)
    B_3_BoostOverCost = ListByListDivide(B_3_Delta_boost, B_3_Tcost)
    B_4_BoostOverCost = ListByListDivide(B_4_Delta_boost, B_4_Tcost)
    C_1_BoostOverCost = ListByListDivide(C_1_Delta_boost, C_1_Tcost)

#    print("DeltaBoost/Cost")
#    ListPrint(C_1_BoostOverCost)
    # add some ID tags to the lists
    A_1_BoostOverCost = [[i + 1, val, "A_1"] for i, val in enumerate(A_1_BoostOverCost)]
    B_1_BoostOverCost = [[i + 1, val, "B_1"] for i, val in enumerate(B_1_BoostOverCost)]
    B_2_BoostOverCost = [[i + 1, val, "B_2"] for i, val in enumerate(B_2_BoostOverCost)]
    B_3_BoostOverCost = [[i + 1, val, "B_3"] for i, val in enumerate(B_3_BoostOverCost)]
    B_4_BoostOverCost = [[i + 1, val, "B_4"] for i, val in enumerate(B_4_BoostOverCost)]
    C_1_BoostOverCost = [[i + 1, val, "C_1"] for i, val in enumerate(C_1_BoostOverCost)]

    # sort in descending order for total damage / cost    
    A_1_BoostOverCost = sorted(A_1_BoostOverCost, key=lambda x: x[1], reverse = True)
    B_1_BoostOverCost = sorted(B_1_BoostOverCost, key=lambda x: x[1], reverse = True)
    B_2_BoostOverCost = sorted(B_2_BoostOverCost, key=lambda x: x[1], reverse = True)
    B_3_BoostOverCost = sorted(B_3_BoostOverCost, key=lambda x: x[1], reverse = True)
    B_4_BoostOverCost = sorted(B_4_BoostOverCost, key=lambda x: x[1], reverse = True)
    C_1_BoostOverCost = sorted(C_1_BoostOverCost, key=lambda x: x[1], reverse = True)

    A_1_BoostOverCost_Filtered = SequentialFilter(A_1_BoostOverCost)
    B_1_BoostOverCost_Filtered = SequentialFilter(B_1_BoostOverCost)
    B_2_BoostOverCost_Filtered = SequentialFilter(B_2_BoostOverCost)
    B_3_BoostOverCost_Filtered = SequentialFilter(B_3_BoostOverCost)
    B_4_BoostOverCost_Filtered = SequentialFilter(B_4_BoostOverCost)
    C_1_BoostOverCost_Filtered = SequentialFilter(C_1_BoostOverCost)

    # fuse all the lists
    MegaList = A_1_BoostOverCost_Filtered + B_1_BoostOverCost_Filtered + B_2_BoostOverCost_Filtered + B_3_BoostOverCost_Filtered + B_4_BoostOverCost_Filtered +  C_1_BoostOverCost_Filtered
    # sort by efficiency
    MegaList = sorted(MegaList, key=lambda x: x[1], reverse = True)
            
    # The first entry on the compressed list is a single entry, record the level changes, repeat the process, until everything is level 30
    if MegaList[0][2]   == "A_1":
        A_1_Current = MegaList[0][0]
    elif MegaList[0][2] == "B_1":
        B_1_Current = MegaList[0][0]
    elif MegaList[0][2] == "B_2":
        B_2_Current = MegaList[0][0]
    elif MegaList[0][2] == "B_3":
        B_3_Current = MegaList[0][0]
    elif MegaList[0][2] == "B_4":
        B_4_Current = MegaList[0][0]
    elif MegaList[0][2] == "C_1":
        C_1_Current = MegaList[0][0]
        
    Final_List.append(MegaList[0])

if Hexa_Stat_Include == True:
    Average_Costs = [
    [323,5],                   # 5 or lower
    [617,6],                   # At least 6
    [1148,7],                  # At least 7
    [3030,8],                  # At least 8
    [12609,9],                 # At least 9
    [145126,10]                # At least 10
    ]

    Stat_Values = {
        'Crit Damage': 0.07,
        'Boss Damage': 0.20,
        'Ignore Def': 0.20,
        'Reg Damage': 0.15,
        'Attack': 100,
        'Stat': 2000
    }

    Stat_dict = {
        'Damage': Damage,
        'Ignore Def': IED,
        'Crit Damage': Crit_Dmg,
        'Attack': Att_Power / (1 + Att_Perc),
        'Stat': Stat
    }

    # print(Stat_dict)
    #               0     1     2     3     4     5     6     7     8     9    10
    Stat_Costs = [10.0, 10.0, 10.0, 20.0, 20.0, 20.0, 20.0, 30.0, 40.0, 50.0, 50.0]
    Main_Prob  = [0.35, 0.35, 0.35, 0.20, 0.20, 0.20, 0.20, 0.15, 0.10, 0.05, 0.00]
    #               0     1     2     3     4     5     6     7     8     9     10
    Main_Multi = [0.00, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.65, 0.80, 1.00]
    Alt_Multi  = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

    if Hexa_Maxed == True:
        if Hexa_Stat_Main[1] == 'Boss Damage' or Hexa_Stat_Main[1] == 'Reg Damage':
            Stat_dict_tag_Main = 'Damage'
        else:
            Stat_dict_tag_Main = Hexa_Stat_Main[1]

        if Hexa_Stat_Alt_0[1] == 'Boss Damage' or Hexa_Stat_Alt_0[1] == 'Reg Damage':
            Stat_dict_tag_Alt_0 = 'Damage'
        else:
            Stat_dict_tag_Alt_0 = Hexa_Stat_Alt_0[1]

        if Hexa_Stat_Alt_1[1] == 'Boss Damage' or Hexa_Stat_Alt_1[1] == 'Reg Damage':
            Stat_dict_tag_Alt_1 = 'Damage'
        else:
            Stat_dict_tag_Alt_1 = Hexa_Stat_Alt_1[1]
            
        # if hexa stats are already being used, then we need to recover the unmodified values
        Stat_dict[Stat_dict_tag_Main] = GiveMeCleanValues(True,Stat_dict.get(Stat_dict_tag_Main),Hexa_Stat_Main[0],Hexa_Stat_Main[1])
        Stat_dict[Stat_dict_tag_Alt_0] = GiveMeCleanValues(False,Stat_dict.get(Stat_dict_tag_Alt_0),Hexa_Stat_Alt_0[0],Hexa_Stat_Alt_0[1])
        Stat_dict[Stat_dict_tag_Alt_1] = GiveMeCleanValues(False,Stat_dict.get(Stat_dict_tag_Alt_1),Hexa_Stat_Alt_1[0],Hexa_Stat_Alt_1[1])

    # print(Stat_dict)
    Crit_Main_Mod = (Stat_Values['Crit Damage'] + 1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2) / (1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2)
    Boss_Main_Mod = (Stat_Values['Boss Damage'] + Stat_dict['Damage'] + 1) / (Stat_dict['Damage'] + 1)
    IED_Main_Mod  =((Stat_Values['Ignore Def'] - 1)*Boss_Def*(1-Stat_dict['Ignore Def'])*(1-Hidden_IED)+1) / (1-Boss_Def*(1-Stat_dict['Ignore Def'])*(1-Hidden_IED))
    Dmg_Main_Mod  = (Stat_Values['Reg Damage'] + Stat_dict['Damage'] + 1) / (Stat_dict['Damage'] + 1)
    Att_Main_Mod  = (Stat_Values['Attack'] + Stat_dict['Attack']) / Stat_dict['Attack']
    Stat_Main_Mod = (Stat_Values['Stat'] + Stat_dict['Stat']) / Stat_dict['Stat']

    Gains = {
        'Crit Damage'   :Crit_Main_Mod,
        'Boss Damage'   :Boss_Main_Mod,
        'Ignore Def'    :IED_Main_Mod,
        'Reg Damage'    :Dmg_Main_Mod,
        'Attack'        :Att_Main_Mod,
        'Stat'          :Stat_Main_Mod
    }

    print("Order of priority")
    Gains = dict(sorted(Gains.items(), key=lambda item: item[1], reverse=True))
    for key, value in Gains.items():
        print(f"{key}: {value}")

    print("")

    Best_Value_Main = []
    Best_Value_Alt_0 = []
    Best_Value_Alt_1 = []
    Damage_Over_Cost = []
    Refined_List = []

    # Damage boost if main level X
    for i in range(len(Main_Multi)):
        Multi_mod = Main_Multi[i]
        Crit_Main_Mod = (Stat_Values['Crit Damage'] * Multi_mod + 1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2) / (1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2)
        Boss_Main_Mod = (Stat_Values['Boss Damage'] * Multi_mod + Stat_dict['Damage'] + 1) / (Stat_dict['Damage'] + 1)
        IED_Main_Mod  =((Stat_Values['Ignore Def'] * Multi_mod - 1)*Boss_Def*(1-Stat_dict['Ignore Def'])*(1-Hidden_IED)+1) / (1-Boss_Def*(1-Stat_dict['Ignore Def'])*(1-Hidden_IED))
        Dmg_Main_Mod  = (Stat_Values['Reg Damage'] * Multi_mod + Stat_dict['Damage'] + 1) / (Stat_dict['Damage'] + 1)
        Att_Main_Mod  = (Stat_Values['Attack'] * Multi_mod + Stat_dict['Attack']) / Stat_dict['Attack']
        Stat_Main_Mod = (Stat_Values['Stat'] * Multi_mod + Stat_dict['Stat']) / Stat_dict['Stat']
        
        Gain_Values = [
            [Crit_Main_Mod, 'Crit Damage'],
            [Boss_Main_Mod, 'Boss Damage'],
            [IED_Main_Mod, 'Ignore Def'],
            [Dmg_Main_Mod, 'Reg Damage'],
            [Att_Main_Mod, 'Attack'],
            [Stat_Main_Mod, 'Stat']
        ]

        Gain_Values = sorted(Gain_Values, key=lambda x: x[0], reverse = True)
        Gain_Values[0].append(i)
        Best_Value_Main.append(Gain_Values[0])

    # Damage boost if alt level X
    for i in range(len(Alt_Multi)):
        Multi_mod = Alt_Multi[i]
        Crit_Main_Mod = (Stat_Values['Crit Damage'] * Multi_mod + 1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2) / (1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2)
        Boss_Main_Mod = (Stat_Values['Boss Damage'] * Multi_mod + Stat_dict['Damage'] + 1) / (Stat_dict['Damage'] + 1)
        IED_Main_Mod  =((Stat_Values['Ignore Def'] * Multi_mod - 1)*Boss_Def*(1-Stat_dict['Ignore Def'])*(1-Hidden_IED)+1) / (1-Boss_Def*(1-Stat_dict['Ignore Def'])*(1-Hidden_IED))
        Dmg_Main_Mod  = (Stat_Values['Reg Damage'] * Multi_mod + Stat_dict['Damage'] + 1) / (Stat_dict['Damage'] + 1)
        Att_Main_Mod  = (Stat_Values['Attack'] * Multi_mod + Stat_dict['Attack']) / Stat_dict['Attack']
        Stat_Main_Mod = (Stat_Values['Stat'] * Multi_mod + Stat_dict['Stat']) / Stat_dict['Stat']
        
        Gain_Values = [
            [Crit_Main_Mod, 'Crit Damage'],
            [Boss_Main_Mod, 'Boss Damage'],
            [IED_Main_Mod, 'Ignore Def'],
            [Dmg_Main_Mod, 'Reg Damage'],
            [Att_Main_Mod, 'Attack'],
            [Stat_Main_Mod, 'Stat']
        ]

        Gain_Values = sorted(Gain_Values, key=lambda x: x[0], reverse = True)
        Gain_Values[1].append(i)
        Best_Value_Alt_0.append(Gain_Values[1])
        Gain_Values[2].append(i)
        Best_Value_Alt_1.append(Gain_Values[2])

        # Damage boost if leveling up
    if Hexa_Maxed == False:
        for i in range(len(Main_Multi)):
            # modulate how much the level up costs
            Total_Cost = Stat_Costs[i]
            # quantify the average damage gained by leveling up
            Main_Delta_Boost = ((Best_Value_Main[i][0] - 1) - (Best_Value_Main[i-1][0] - 1)) * Main_Prob[i]
            Alt_0_Delta_Boost = ((Best_Value_Alt_0[i][0] - 1) - (Best_Value_Alt_0[i-1][0] - 1)) * (1-Main_Prob[i])/2
            Alt_1_Delta_Boost = ((Best_Value_Alt_1[i][0] - 1) - (Best_Value_Alt_1[i-1][0] - 1)) * (1-Main_Prob[i])/2

            if i == 0:
                Main_Delta_Boost = (Best_Value_Main[i+1][0] - 1) * Main_Prob[i]
                Alt_0_Delta_Boost = (Best_Value_Alt_0[i+1][0] - 1) * (1-Main_Prob[i])/2
                Alt_1_Delta_Boost = (Best_Value_Alt_1[i+1][0] - 1) * (1-Main_Prob[i])/2
                
            Delta_Boost = Main_Delta_Boost + Alt_0_Delta_Boost + Alt_1_Delta_Boost
                
            Add_To_List = [i, Delta_Boost / Total_Cost, "Stat Core"]
            Damage_Over_Cost.append(Add_To_List)

        DOC_Compressed = []
        for i in range(len(Damage_Over_Cost)):
            Damage_Over_Cost[i][1] = round(Damage_Over_Cost[i][1],16)
            if i > 0:
                if Damage_Over_Cost[i][1] != Damage_Over_Cost[i-1][1]:
                    DOC_Compressed.append(Damage_Over_Cost[i-1])

        DOC_Filtered = []
        DOC_Point_Tracker = []
        for i in range(len(DOC_Compressed)):
            if i > 0:
                if DOC_Compressed[i][1] <= DOC_Compressed[i-1][1]:
                    DOC_Filtered.append(DOC_Compressed[i-1])
                else:
                    DOC_Point_Tracker.append(i)
        if DOC_Compressed[-1][1] <= DOC_Filtered[-1][1]:
            DOC_Filtered.append(DOC_Compressed[i])

        for i in range(len(DOC_Point_Tracker)):
            DOC_Filtered[DOC_Point_Tracker[i]-1][1] = DOC_Compressed[DOC_Point_Tracker[i]-1][1]

        for i in range(len(DOC_Filtered)):
            DOC_Filtered[i][0] = "Until " + str(DOC_Filtered[i][0] + 1)

        DOC_Filtered[-1][0] = "Max it"
        
        Final_List = Final_List + DOC_Filtered
        Final_List = sorted(Final_List, key=lambda x: x[1], reverse = True)
    else:
        # Damage boost if refining
        Main_key, Main_Value = list(Gains.items())[0]
        Alt_0_key, Alt_0_Value = list(Gains.items())[1]
        Alt_1_key, Alt_1_Value = list(Gains.items())[2]
    #    print(Main_key, Main_Value)
    #    print(Alt_0_key, Alt_0_Value)
    #    print(Alt_1_key, Alt_1_Value)
        
        Multi_Values = [Main_Multi[Hexa_Stat_Main[0]], Alt_Multi[Hexa_Stat_Alt_0[0]], Alt_Multi[Hexa_Stat_Alt_1[0]]]
        Multi_Values = sorted(Multi_Values, reverse=True)
        Old_Boost0 = (Main_Value - 1) * Multi_Values[0]
        Old_Boost1 = (Alt_0_Value - 1) * Multi_Values[1]
        Old_Boost2 = (Alt_1_Value - 1) * Multi_Values[2]
        Old_Boost = Old_Boost0 + Old_Boost1 + Old_Boost2
        print(Old_Boost)
    #    print(Multi_Values)

        min_refine = Hexa_Stat_Main[0]
        if Hexa_Stat_Main[0] <= Average_Costs[0][1]:
            min_refine = Average_Costs[0][1] + 1
        for i in range(min_refine,len(Main_Multi)):
            Max = 20
            Main_Boost  = 0
            Alt_Level_0 = 0
            Alt_Level_1 = 0
            if (Max - i) % 2 == 0:
                Alt_Level_0 = (Max - i) / 2
                Alt_Level_1 = (Max - i) / 2
            else:
                Alt_Level_0 = (Max - i + 1) / 2
                Alt_Level_1 = (Max - i - 1) / 2    
                
            Alt_Boost_0 = Alt_Multi[int(Alt_Level_0)]
            Alt_Boost_1 = Alt_Multi[int(Alt_Level_1)]
            Multi_Values = [Main_Multi[i], Alt_Boost_0, Alt_Boost_1]
            Multi_Values = sorted(Multi_Values, reverse=True)
    #        print(Multi_Values)
            
            Total_Boost = (Main_Value-1)*Multi_Values[0] + (Alt_0_Value-1)*Multi_Values[1] + (Alt_1_Value-1)*Multi_Values[2]
            
            if i < Average_Costs[0][1]:
                Total_Cost = Average_Costs[0][0]
            else:
                Total_Cost = Average_Costs[i - Average_Costs[0][1]][0]
                
    #        print(str(i) + "    " + str(Total_Cost))
            Add_To_List = [i,(Total_Boost - Old_Boost)/ Total_Cost, "Stat Core"]
            Refined_List.append(Add_To_List)
            
            for i in range(len(Refined_List)):
                if Refined_List[i][1] <= 0:
                    del Refined_List[i]
            
        Final_List = Final_List + Refined_List
        Final_List = sorted(Final_List, key=lambda x: x[1], reverse = True)
###

# merge any consecutive patterns A_1 [0,1,2,3,4,5] -> A_1 [5]
Compressed_Final_List = [Final_List[0]]  # Initialize with the first element
for i in range(1, len(Final_List)):
    current_element = Final_List[i]
    previous_element = Compressed_Final_List[-1]
 
# Check if the current element's third element is different from the previous one
    if current_element[2] == previous_element[2]:
        Compressed_Final_List[-1] = current_element
    else:
        Compressed_Final_List.append(current_element)
             
#    print("next")
ListPrint(Compressed_Final_List)
# printing stuff

grid_width, grid_height = 10, 4  # You can adjust these dimensions as needed
spacing = 20

# Calculate the size of each image and the spacing
image_size = 64  # Adjust the spacing (10) as needed

# Define the canvas size and grid dimensions
canvas_height = grid_height * (spacing + image_size) + 150
canvas_width  = 1200

while len(Compressed_Final_List) >= grid_width * grid_height:
    grid_height += 1
    canvas_height += image_size + spacing

if canvas_width < (16 / 9) * canvas_height:
    canvas_width = round(16 / 9 * canvas_height)
    
# Get the current working directory
current_directory = os.getcwd()

# Construct paths for image files
image_A_1 = Image.open(os.path.join(current_directory, "A_1.png"))
image_B_1 = Image.open(os.path.join(current_directory, "B_1.png"))
image_B_2 = Image.open(os.path.join(current_directory, "B_2.png"))
image_B_3 = Image.open(os.path.join(current_directory, "B_3.png"))
image_B_4 = Image.open(os.path.join(current_directory, "B_4.png"))
image_C_1 = Image.open(os.path.join(current_directory, "C_1.png"))
image_Stat = Image.open(os.path.join(current_directory, "Stat.png"))

background_image = Image.open("Background.png")

# Create a blank canvas with the same size as the background image
canvas = Image.new("RGB", (canvas_width, canvas_height))

# Paste the background image onto the canvas
canvas.paste(background_image.resize((canvas_width, canvas_height)), (0, 0))

# Create a drawing object to draw on the canvas
draw = ImageDraw.Draw(canvas)

# Define the font size and border size for the numbers
font_size = 24
border_size = 2

if FragBase == True:
    supplementary_title = "(Fragments)"
else:
    supplementary_title = "(Energy)"
    
title_text = "Dark Knight 6th Job Optimization GMS " + supplementary_title 
author_text = "By: LazyVista (XseedGames)"
if Hexa_Stat_Include == True:
    if Hexa_Maxed == False:
        priority_text = "No Rerolling --- " + list(Gains.items())[0][0] + " / " + list(Gains.items())[1][0] + " / " + list(Gains.items())[2][0]
    else:
        priority_text = "Rerolling Style --- " + list(Gains.items())[0][0] + " / " + list(Gains.items())[1][0] + " / " + list(Gains.items())[2][0]
title_font_size = 36  # Adjust to your desired font size
author_font_size = 24  # Adjust to your desired font size
tile_border_size = 2

x_base_shift = int(canvas_width / 2)  - (image_size + spacing)*int(grid_width / 2)
y_base_shift = 125

entry = 0

# draw title
font = ImageFont.truetype("arial.ttf", title_font_size)  # You can change the font family
text_width = draw.textlength(title_text, font)
text_height = 0
x = (canvas_width - text_width) // 2
y = 10  # You can adjust the Y position for the title
text_position = (x, y)

border_color = (0, 0, 0)  # Black border color
for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
        if dx != 0 or dy != 0:
            border_position = (text_position[0] + dx * border_size, text_position[1] + dy * border_size)
            draw.text(border_position, title_text, fill=border_color, font=font)

draw.text(text_position, title_text, fill=(255, 255, 255), font=font)  # Adjust the text color as needed

# draw authorship
font = ImageFont.truetype("arial.ttf", author_font_size)  # You can change the font family
text_width = draw.textlength(author_text, font)
text_height = 0
x = (canvas_width - text_width) // 2
y = 70  # You can adjust the Y position for the title
text_position = (x, y)

border_color = (0, 0, 0)  # Black border color
for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
        if dx != 0 or dy != 0:
            border_position = (text_position[0] + dx * border_size, text_position[1] + dy * border_size)
            draw.text(border_position, author_text, fill=border_color, font=font)

draw.text(text_position, author_text, fill=(255, 255, 255), font=font)  # Adjust the text color as needed

# draw hexa info
if Hexa_Stat_Include == True:
    font = ImageFont.truetype("arial.ttf", author_font_size)  # You can change the font family
    text_width = draw.textlength(priority_text, font)
    text_height = 0
    x = (canvas_width - text_width) // 2
    y = canvas_height - 30  # You can adjust the Y position for the title
    text_position = (x, y)

    border_color = (0, 0, 0)  # Black border color
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                border_position = (text_position[0] + dx * border_size, text_position[1] + dy * border_size)
                draw.text(border_position, priority_text, fill=border_color, font=font)

    draw.text(text_position, priority_text, fill=(255, 255, 255), font=font)  # Adjust the text color as needed

for row in range(grid_height):
    for col in range(grid_width):
        x = col * (image_size + spacing) + x_base_shift # Adjust the spacing (10) as needed
        y = row * (image_size + spacing) + y_base_shift # Adjust the spacing (10) as needed

        # Paste the "Draw.png" file into the canvas
        if Compressed_Final_List[entry][2] == "A_1":
            canvas.paste(image_A_1.resize((image_size, image_size)), (x, y))
        elif Compressed_Final_List[entry][2] == "B_1":
            canvas.paste(image_B_1.resize((image_size, image_size)), (x, y))
        elif Compressed_Final_List[entry][2] == "B_2":
            canvas.paste(image_B_2.resize((image_size, image_size)), (x, y))
        elif Compressed_Final_List[entry][2] == "B_3":
            canvas.paste(image_B_3.resize((image_size, image_size)), (x, y))
        elif Compressed_Final_List[entry][2] == "B_4":
            canvas.paste(image_B_4.resize((image_size, image_size)), (x, y))
        elif Compressed_Final_List[entry][2] == "C_1":
            canvas.paste(image_C_1.resize((image_size, image_size)), (x, y))
        elif Compressed_Final_List[entry][2] == "Stat Core":
            canvas.paste(image_Stat.resize((image_size, image_size)), (x, y))
            
        Result_lv = Compressed_Final_List[entry][0]

        # Calculate the position for the text
        if isinstance(Result_lv, int):
            text_position = (x + 15, y + 45)  # Adjust the position as needed
        else:
            text_position = (x, y + 45)  # Adjust the position as needed

        # Create a font and draw the black border
        font = ImageFont.truetype("arial.ttf", font_size)
        border_color = (0, 0, 0)  # Black border color
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    border_position = (text_position[0] + dx * border_size, text_position[1] + dy * border_size)
                    if isinstance(Result_lv, int):
                        draw.text(border_position, f"lv. {Result_lv}", fill=border_color, font=font)
                    else:
                        draw.text(border_position, f"{Result_lv}", fill=border_color, font=font)

        # Draw the text on top of the border
        if isinstance(Result_lv, int):
            draw.text(text_position, f"lv. {Result_lv}", fill=(255, 255, 255), font=font)
        else:
            draw.text(text_position, f"{Result_lv}", fill=(255, 255, 255), font=font)
        entry += 1
        if entry == len(Compressed_Final_List):
            break
    if entry == len(Compressed_Final_List):
        break

# Save the final canvas image
canvas.save("Optimized.png")

# Optionally, display the image
canvas.show()


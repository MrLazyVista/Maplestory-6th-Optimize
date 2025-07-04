from PIL import Image, ImageDraw, ImageFont
import os
import copy
import numpy
import tkinter as tk

# If you want to customize the code to a class that isnt Dark Knight 
# 1. Make the mastery skill percentages match your class
# 2. Ctrl + F "def Fill_Boost" change the skill percentages to match the mastery numbers
# 3. Ctrl + F "Reverter_Multi(Damage_Distribution" and use Reverter for skills that dont have multiple masteries affecting them, and multi version for those that do
# 4. Replace the skill .png in the folder this python code is in

## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... Level_Distribution['C_1_Level'])
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... Level_Distribution['C_1_Level'])
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... Level_Distribution['C_1_Level'])
# Fragment based optimization Toggle_Stuff['Frag_Base'] = True
# Energy based optimization Toggle_Stuff['Frag_Base'] = False
# Optimize for rerolling Hexa Core = True
Toggle_Stuff = {
    'Frag_Base'         :True,
    'Hexa_Stat_Include' :True,
    'Hexa_Maxed'        :False,
    'ForceMasteryA1234' :True,
    }
    
# Use percentage values 98% = 98, 612% = 612, etc etc
# Damage is Boss% + Damage%,
# IED is what you see on character sheet
# Hidden IED is IED that doesnt show up on your character page, explorer link, built into skills, debuffs, etc etc
Base_Numbers = {
    'Damage'    :500+90+80,
    'IED'       :97,
    'Hidden_IED':40,
    'Boss_Def'  :380
    }

# Fill out your Battle Analysis Contributions in this table and dont forget the levels as well
# Use percentage values 15% = 15, same as above.
# A skills are "Mastery Skills", B Skills are Reinforcements, C Skills are Origin Skills
# Some mastery skills have overlapping skills, thats why you see the "Damage_Distribution['A_1']"

Damage_Distribution = {}
Damage_Distribution['A_1']  = 14.99                             # Gungnir

Damage_Distribution['A_2a'] = Damage_Distribution['A_1']        # Also Gungnir
Damage_Distribution['A_2b'] = 3.16                              # Nightshade
Damage_Distribution['A_2c'] = 0                                 # Impale

Damage_Distribution['A_3a'] = 7.52                              # EE Revenge
Damage_Distribution['A_3b'] = 2.01                              # EE Punishment
Damage_Distribution['A_3c'] = 1.75                              # Final Attack

Damage_Distribution['A_4a'] = 3.96                              # EE Shock
Damage_Distribution['A_4b'] = Damage_Distribution['A_2b']       # Nightshade
Damage_Distribution['A_4c'] = Damage_Distribution['A_3a']       # EE Revenge
Damage_Distribution['A_4d'] = Damage_Distribution['A_3b']       # EE Punishment

Damage_Distribution['B_1'] = 22.00                              # Soear
Damage_Distribution['B_2'] = 9.83                               # Radiant
Damage_Distribution['B_3'] = 8.33                               # Cyclone
Damage_Distribution['B_4'] = 6.85                               # Darkness Aura

Damage_Distribution['C_1'] = 5.45                               # Dead Space

# Current Skill Levels (6th Core)
Level_Distribution = {
    'A_1_Level': 0,
    'A_2_Level': 0,
    'A_3_Level': 0,
    'A_4_Level': 0,
    'B_1_Level': 0,
    'B_2_Level': 0,
    'B_3_Level': 0,
    'B_4_Level': 0,
    'C_1_Level': 1,
}

# These stats (Crit_Dmg, Att_Power, Att_Perc, Stat) are only used if Toggle_Stuff['Hexa_Stat_Include'] is True
Additional_Numbers = {
    'Crit_Dmg'  :130 + 30,
    'Att_Power' :7000,
    'Att_Perc'  :97,
    'Stat'      :74000
    }

# Hexa_Stat_ Main/Alt values are only used if Toggle_Stuff['Hexa_Maxed'] is True, uses a [level,Stat] format, use the following strings of "Stat"
# 'Crit Damage','Boss Damage','Ignore Def','Reg Damage','Attack','Stat'
Hexa_Stat_Main  = [6 , 'Stat']
Hexa_Stat_Alt_0 = [10, 'Attack']
Hexa_Stat_Alt_1 = [4 , 'Crit Damage']

## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... Level_Distribution['C_1_Level'])
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... Level_Distribution['C_1_Level'])
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... Level_Distribution['C_1_Level'])
## You can ignore everything below here, let the magic machine do its work

# Damage gain vs level
def Fill_Boost(List,ID,Aux,Val,Start,End):
    sig_fig     = 8
    for i in range(Start,End):
        if   ID == "A1":
            # should be adjusted to match class specific values (although most are gonna be similiar
            Aux_IED     = (1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])*(1-(0.3 + int(i/30*10)/100))*(1-.2))/(1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])*(1-0.3)*(1-.2))
            List[i]     = ((225 + 15 +5*(i+1))/225 * Aux * Aux_IED - 1) * Val
            # just incase I use the same name somewhere else
            Aux_IED = 1
        elif ID == "A2a":   
            List[i]   = ((225 + 55 + 3*(i+1))/225 * Aux - 1) * Val
        elif ID == "A2b":
            Aux_IED   = (1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])*(1-0.6))/(1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED']))
            Aux_Boss  = (1 + Base_Numbers['Damage'] + .3) / (1 + Base_Numbers['Damage'])
            List[i]   = (((390 + 12*(i+1))*12/10)/400 * Aux * Aux_IED * Aux_Boss - 1) * Val
            Aux_IED   = 1
            Aux_Boss  = 1
        elif ID == "A2c":   
            List[i]   = ((298 + 9*(i+1))/280 * Aux - 1) * Val
        elif ID == "A3a":   
            List[i]   = ((88 + 2*(i+1))/88 * Aux - 1) * Val
        elif ID == "A3b":   
            List[i]   = ((143 + 3*(i+1))/143 * Aux - 1) * Val
        elif ID == "A3c":
            Proc_Per  = (40+(i+1)*25/30)/40
            List[i]   = (Proc_Per*(87 + 1*(i+1))/80 * Aux - 1) * Val
        elif ID == "A4a":   
            List[i]   = ((((680 + 20*(i+1))/630) * Aux - 1)+(((470 + 13*(i+1))/423) * Aux - 1))/2 * Val
        elif ID == "A4b":   
            List[i]   = (((390 + 37 + 9*(i+1))*12/10)/400 * Aux - 1) * Val
        elif ID == "A4c":   
            List[i]   = ((88 + 7 + 1*(i+1))/88 * Aux - 1) * Val
        elif ID == "A4d":   
            List[i]   = ((143 + 15 + 4/3*(i+1))/143 * Aux - 1) * Val
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
                List[i] = Damage_Distribution['C_1']
            elif (i+1) < 10:
                CAux     = 1
                List[i] = Damage_Distribution['C_1'] + round((i) * Aux * CAux * Val/30,sig_fig)
            elif (i+1) < 20:
                CAux     = (1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])*(1-.2))/(1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED']))
                List[i] = Damage_Distribution['C_1'] + round((i) * Aux * CAux  * Val/30,sig_fig)
            elif (i+1) < 30:
                CAux     = (1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])*(1-.2))/(1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])) * (1 + Base_Numbers['Damage'] + .2) / (1 + Base_Numbers['Damage'])
                List[i] = Damage_Distribution['C_1'] + round((i) * Aux * CAux  * Val/30,sig_fig)
            elif (i+1) == 30:
                CAux     = (1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])*(1-.2)*(1-0.3))/(1-Base_Numbers['Boss_Def']*(1-Base_Numbers['IED'])) * (1 + Base_Numbers['Damage'] + .2 + .3) / (1 + Base_Numbers['Damage'])
                List[i] = Damage_Distribution['C_1'] + round((i) * Aux * CAux  * Val/30,sig_fig)
    return List
    
# for debugging purposes
def ListPrint(List):
    # Determine the maximum width for each column
    max_lengths = [max(len(str(item)) for sublist in List for item in sublist)]

    # Print each row with formatted columns
    for row in List:
        formatted_row = ' '.join('{:<{width}}'.format(item, width=max_lengths[0]+1) for item in row)
        print(formatted_row)
        
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
        A += List[Level-1]
    B = Value / A
    C = Value - B
    return B, C
    
def Reverter_Multi(Value,Level_a,List_a,Level_b,List_b):
    A = 1
    if Level_a > 0:
        A += List_a[Level_a-1]
        if Level_b > 0:
            A += List_b[Level_b-1]
    B = Value / A
    C = Value - B
    return B, C


def GiveMeCleanValues(Main,Stat_Values,Main_Multi,Alt_Multi,Current,Level,Type):
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

def sum_entries_up_to_number(lst, num):
    # Use list slicing to get the sublist from index 0 to num
    sublist = lst[:num + 1]
    
    # Use the sum() function to calculate the sum of the sublist
    total_sum = sum(sublist)
    
    return total_sum

def Run_Main():
    for key in Base_Numbers:
        Base_Numbers[key] /= 100
    
    for key in Damage_Distribution:
        Damage_Distribution[key] /= 100

    Additional_Numbers['Crit_Dmg'] /= 100
    Additional_Numbers['Att_Perc'] /= 100
    
    if Toggle_Stuff['Frag_Base']:
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
        ,128
        ,135
        ,143
        ,150
        ,158
        ,165
        ,173
        ,180
        ,188
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
    A_2a_boost   = 30 * [0]
    A_2b_boost   = 30 * [0]
    A_2c_boost   = 30 * [0]
    A_2_boost   = 30 * [0]
    A_3a_boost   = 30 * [0]
    A_3b_boost   = 30 * [0]
    A_3c_boost   = 30 * [0]
    A_3_boost   = 30 * [0]
    A_4a_boost   = 30 * [0]
    A_4b_boost   = 30 * [0]
    A_4c_boost   = 30 * [0]
    A_4d_boost   = 30 * [0]
    A_4_boost   = 30 * [0]
    B_1_boost   = 30 * [0]
    B_2_boost   = 30 * [0]
    B_3_boost   = 30 * [0]
    B_4_boost   = 30 * [0]
    C_1_boost   = 30 * [0]
    BoostArray  = {
        'A_1'   :   0,
        'A_2'   :   0,
        'A_3'   :   0,
        'A_4'   :   0,
        'B_1'   :   0,
        'B_2'   :   0,
        'B_3'   :   0,
        'B_4'   :   0,
        'C_1'   :   0,
        }
    CostArray   = {
        'A_1'   :   0,
        'A_2'   :   0,
        'A_3'   :   0,
        'A_4'   :   0,
        'B_1'   :   0,
        'B_2'   :   0,
        'B_3'   :   0,
        'B_4'   :   0,
        'C_1'   :   0,
        }
    Final_List  = []
    C_1_Changed = False

    # Mod Values are the skill BA contributions if there were no 6th progress except for origin(makes the math simplier)
    # if Level_Distribution['C_1_Level'] = 0 then that means you got a naked skill tree so everything is by default 0
    # if C_1 does not equal zero then, some conversions will have to be done
    if Level_Distribution['C_1_Level'] == 0:
        Level_Distribution['C_1_Level'] = 1
        C_1_Changed = True
        Amod_1  = Damage_Distribution['A_1'] / ( 1 + Damage_Distribution['C_1'])
        
        Amod_2a = Damage_Distribution['A_2a'] / ( 1 + Damage_Distribution['C_1'])
        Amod_2b = Damage_Distribution['A_2b'] / ( 1 + Damage_Distribution['C_1'])
        Amod_2c = Damage_Distribution['A_2c'] / ( 1 + Damage_Distribution['C_1'])
        
        Amod_3a = Damage_Distribution['A_3a'] / ( 1 + Damage_Distribution['C_1'])
        Amod_3b = Damage_Distribution['A_3b'] / ( 1 + Damage_Distribution['C_1'])
        Amod_3c = Damage_Distribution['A_3c'] / ( 1 + Damage_Distribution['C_1'])
        
        Amod_4a = Damage_Distribution['A_4a'] / ( 1 + Damage_Distribution['C_1'])
        Amod_4b = Damage_Distribution['A_4b'] / ( 1 + Damage_Distribution['C_1'])
        Amod_4c = Damage_Distribution['A_4c'] / ( 1 + Damage_Distribution['C_1'])
        Amod_4d = Damage_Distribution['A_4d'] / ( 1 + Damage_Distribution['C_1'])
        
        Bmod_1  = Damage_Distribution['B_1'] / ( 1 + Damage_Distribution['C_1'])
        Bmod_2  = Damage_Distribution['B_2'] / ( 1 + Damage_Distribution['C_1'])
        Bmod_3  = Damage_Distribution['B_3'] / ( 1 + Damage_Distribution['C_1'])
        Bmod_4  = Damage_Distribution['B_4'] / ( 1 + Damage_Distribution['C_1'])
        
        # in the original script A_1 is for Gungnir(Dark Knight) which has a IED boost component
        # The "Aux" values are multipliers that are meant to compensate for these extra features
        # if there are no auxilary features, just put 1 for the skill
        A_1_Aux         = 1
        A_2_Aux         = 1
        A_3_Aux         = 1
        A_4_Aux         = 1
        B_1_Aux         = 1
        B_2_Aux         = 1
        B_3_Aux         = 1
        B_4_Aux         = 1
        C_1_Aux         = 1
        
        A_1_boost = Fill_Boost(A_1_boost,"A1",A_1_Aux ,Amod_1 ,0  ,len(A_cost))
        
        A_2a_boost = Fill_Boost(A_2a_boost,"A2a",A_2_Aux ,Amod_2a ,0  ,len(A_cost))
        A_2b_boost = Fill_Boost(A_2b_boost,"A2b",A_2_Aux ,Amod_2b ,0  ,len(A_cost))
        A_2c_boost = Fill_Boost(A_2c_boost,"A2c",A_2_Aux ,Amod_2c ,0  ,len(A_cost))
        A_2_boost = [sum(values) for values in zip(A_2a_boost,A_2b_boost,A_2c_boost)]

        A_3a_boost = Fill_Boost(A_3a_boost,"A3a",A_3_Aux ,Amod_3a ,0  ,len(A_cost))
        A_3b_boost = Fill_Boost(A_3b_boost,"A3b",A_3_Aux ,Amod_3b ,0  ,len(A_cost))
        A_3c_boost = Fill_Boost(A_3c_boost,"A3c",A_3_Aux ,Amod_3c ,0  ,len(A_cost))
        A_3_boost = [sum(values) for values in zip(A_3a_boost,A_3b_boost,A_3c_boost)]

        A_4a_boost = Fill_Boost(A_4a_boost,"A4a",A_4_Aux ,Amod_4a ,0  ,len(A_cost))
        A_4b_boost = Fill_Boost(A_4b_boost,"A4b",A_4_Aux ,Amod_4b ,0  ,len(A_cost))
        A_4c_boost = Fill_Boost(A_4c_boost,"A4c",A_4_Aux ,Amod_4c ,0  ,len(A_cost))
        A_4d_boost = Fill_Boost(A_4d_boost,"A4d",A_4_Aux ,Amod_4d ,0  ,len(A_cost))
        A_4_boost = [sum(values) for values in zip(A_4a_boost,A_4b_boost,A_4c_boost,A_4d_boost)]
        
        B_1_boost = Fill_Boost(B_1_boost,"B",B_1_Aux ,Bmod_1 ,0  ,len(B_cost))
        B_2_boost = Fill_Boost(B_2_boost,"B",B_2_Aux ,Bmod_2 ,0  ,len(B_cost))
        B_3_boost = Fill_Boost(B_3_boost,"B",B_3_Aux ,Bmod_3 ,0  ,len(B_cost))
        B_4_boost = Fill_Boost(B_4_boost,"B",B_4_Aux ,Bmod_4 ,0  ,len(B_cost))
        
        C_1_boost = Fill_Boost(C_1_boost,"C",C_1_Aux ,Damage_Distribution['C_1']    ,0  ,len(C_cost))
        
        print('A_1 Base :' + str(round(Amod_1,5)))
        print('A_2a Base :' + str(round(Amod_2a,5)))
        print('A_2b Base :' + str(round(Amod_2b,5)))
        print('A_2c Base :' + str(round(Amod_2c,5)))
        print('A_3a Base :' + str(round(Amod_3a,5)))
        print('A_3b Base :' + str(round(Amod_3b,5)))
        print('A_3c Base :' + str(round(Amod_3c,5)))
        print('A_4a Base :' + str(round(Amod_4a,5)))
        print('A_4b Base :' + str(round(Amod_4b,5)))
        print('A_4c Base :' + str(round(Amod_4c,5)))
        print('A_4d Base :' + str(round(Amod_4d,5)))
        print('B_1 Base :' + str(round(Bmod_1,5)))
        print('B_2 Base :' + str(round(Bmod_2,5)))
        print('B_3 Base :' + str(round(Bmod_3,5)))
        print('B_4 Base :' + str(round(Bmod_4,5)))
        print('C_1 Base :' + str(round(C_1,5)))
    else:
    # where i left off ------------------------------------------
        A_1_Aux         = 1
        A_2_Aux         = 1
        A_3_Aux         = 1
        A_4_Aux         = 1
        B_1_Aux         = 1
        B_2_Aux         = 1
        B_3_Aux         = 1
        B_4_Aux         = 1
        C_1_Aux         = 1
        
        A_1_Multi_boost = Fill_Boost(A_1_boost,"A1",A_1_Aux ,1 ,0  ,len(A_cost))
        
        A_2a_Multi_boost = Fill_Boost(A_2a_boost,"A2a",A_2_Aux ,1 ,0  ,len(A_cost))
        A_2b_Multi_boost = Fill_Boost(A_2b_boost,"A2b",A_2_Aux ,1 ,0  ,len(A_cost))
        A_2c_Multi_boost = Fill_Boost(A_2c_boost,"A2c",A_2_Aux ,1 ,0  ,len(A_cost))

        A_3a_Multi_boost = Fill_Boost(A_3a_boost,"A3a",A_3_Aux ,1 ,0  ,len(A_cost))
        A_3b_Multi_boost = Fill_Boost(A_3b_boost,"A3b",A_3_Aux ,1 ,0  ,len(A_cost))
        A_3c_Multi_boost = Fill_Boost(A_3c_boost,"A3c",A_3_Aux ,1 ,0  ,len(A_cost))
        
        A_4a_Multi_boost = Fill_Boost(A_4a_boost,"A4a",A_4_Aux ,1 ,0  ,len(A_cost))
        A_4b_Multi_boost = Fill_Boost(A_4b_boost,"A4b",A_4_Aux ,1 ,0  ,len(A_cost))
        A_4c_Multi_boost = Fill_Boost(A_4c_boost,"A4c",A_4_Aux ,1 ,0  ,len(A_cost))
        A_4d_Multi_boost = Fill_Boost(A_4c_boost,"A4d",A_4_Aux ,1 ,0  ,len(A_cost))
        
        B_1_Multi_boost = Fill_Boost(B_1_boost,"B",B_1_Aux ,1 ,0  ,len(B_cost))
        B_2_Multi_boost = Fill_Boost(B_2_boost,"B",B_2_Aux ,1 ,0  ,len(B_cost))
        B_3_Multi_boost = Fill_Boost(B_3_boost,"B",B_3_Aux ,1 ,0  ,len(B_cost))
        B_4_Multi_boost = Fill_Boost(B_4_boost,"B",B_4_Aux ,1 ,0  ,len(B_cost))
        
        C_1_Multi_boost = Fill_Boost(C_1_boost,"C",C_1_Aux ,1 ,0  ,len(C_cost))
        C_1_Multi_boost = [x - C_1_Multi_boost[0] for x in C_1_Multi_boost]
        
        Revert_Amod_1,Delta_A_1    = Reverter_Multi(Damage_Distribution['A_1'] ,Level_Distribution['A_1_Level'],A_1_Multi_boost,Level_Distribution['A_2_Level'],A_2a_Multi_boost)
        
        Revert_Amod_2a,Delta_A_2a  = Reverter_Multi(Damage_Distribution['A_2a'],Level_Distribution['A_1_Level'],A_1_Multi_boost,Level_Distribution['A_2_Level'],A_2a_Multi_boost)
        Revert_Amod_2b,Delta_A_2b  = Reverter_Multi(Damage_Distribution['A_2b'],Level_Distribution['A_2_Level'],A_2b_Multi_boost,Level_Distribution['A_4_Level'],A_4b_Multi_boost)
        Revert_Amod_2c,Delta_A_2c  =       Reverter(Damage_Distribution['A_2c'],Level_Distribution['A_2_Level'],A_2c_Multi_boost)
        
        Revert_Amod_3a,Delta_A_3a  = Reverter_Multi(Damage_Distribution['A_3a'],Level_Distribution['A_3_Level'],A_3a_Multi_boost,Level_Distribution['A_4_Level'],A_4c_Multi_boost)
        Revert_Amod_3b,Delta_A_3b  = Reverter_Multi(Damage_Distribution['A_3b'],Level_Distribution['A_3_Level'],A_3b_Multi_boost,Level_Distribution['A_4_Level'],A_4d_Multi_boost)
        Revert_Amod_3c,Delta_A_3c  =       Reverter(Damage_Distribution['A_3c'],Level_Distribution['A_3_Level'],A_3c_Multi_boost)
        
        Revert_Amod_4a,Delta_A_4a  =       Reverter(Damage_Distribution['A_4a'],Level_Distribution['A_4_Level'],A_4a_Multi_boost)
        Revert_Amod_4b,Delta_A_4b  = Reverter_Multi(Damage_Distribution['A_4b'],Level_Distribution['A_2_Level'],A_2b_Multi_boost,Level_Distribution['A_4_Level'],A_4b_Multi_boost)
        Revert_Amod_4c,Delta_A_4c  = Reverter_Multi(Damage_Distribution['A_4c'],Level_Distribution['A_3_Level'],A_3a_Multi_boost,Level_Distribution['A_4_Level'],A_4c_Multi_boost)
        Revert_Amod_4d,Delta_A_4d  = Reverter_Multi(Damage_Distribution['A_4d'],Level_Distribution['A_3_Level'],A_3b_Multi_boost,Level_Distribution['A_4_Level'],A_4d_Multi_boost)

        Revert_Bmod_1,Delta_B_1  = Reverter(Damage_Distribution['B_1'],Level_Distribution['B_1_Level'],B_1_Multi_boost) 
        Revert_Bmod_2,Delta_B_2  = Reverter(Damage_Distribution['B_2'],Level_Distribution['B_2_Level'],B_2_Multi_boost)
        Revert_Bmod_3,Delta_B_3  = Reverter(Damage_Distribution['B_3'],Level_Distribution['B_3_Level'],B_3_Multi_boost)
        Revert_Bmod_4,Delta_B_4  = Reverter(Damage_Distribution['B_4'],Level_Distribution['B_4_Level'],B_4_Multi_boost)
        Revert_C_1   ,Delta_C_1  = Reverter(Damage_Distribution['C_1'],Level_Distribution['C_1_Level'],C_1_Multi_boost)
            
        Delta_T = Delta_A_1 + Delta_A_2a + Delta_A_2b + Delta_A_2c + Delta_A_3a + Delta_A_3b + Delta_A_3c + Delta_A_4a + Delta_A_4b + Delta_A_4c + Delta_A_4d + Delta_B_1 + Delta_B_2 + Delta_B_3 + Delta_B_4 + Delta_C_1
        
        Amod_1  = Revert_Amod_1 * ( 1 + Delta_T )
        Amod_2a  = Revert_Amod_2a * ( 1 + Delta_T )
        Amod_2b  = Revert_Amod_2b * ( 1 + Delta_T )
        Amod_2c  = Revert_Amod_2c * ( 1 + Delta_T )
        Amod_3a  = Revert_Amod_3a * ( 1 + Delta_T )
        Amod_3b  = Revert_Amod_3b * ( 1 + Delta_T )
        Amod_3c  = Revert_Amod_3c * ( 1 + Delta_T )
        Amod_4a  = Revert_Amod_4a * ( 1 + Delta_T )
        Amod_4b  = Revert_Amod_4b * ( 1 + Delta_T )
        Amod_4c  = Revert_Amod_4c * ( 1 + Delta_T )
        Amod_4d  = Revert_Amod_4d * ( 1 + Delta_T )
        Bmod_1  = Revert_Bmod_1 * ( 1 + Delta_T )
        Bmod_2  = Revert_Bmod_2 * ( 1 + Delta_T )
        Bmod_3  = Revert_Bmod_3 * ( 1 + Delta_T )
        Bmod_4  = Revert_Bmod_4 * ( 1 + Delta_T )
        C_1     = Revert_C_1 * ( 1 + Delta_T )
        
        A_1_boost = Fill_Boost(A_1_boost,"A1",A_1_Aux ,Amod_1 ,0  ,len(A_cost))
        
        A_2a_boost = Fill_Boost(A_2a_boost,"A2a",A_2_Aux ,Amod_2a ,0  ,len(A_cost))
        A_2b_boost = Fill_Boost(A_2b_boost,"A2b",A_2_Aux ,Amod_2b ,0  ,len(A_cost))
        A_2c_boost = Fill_Boost(A_2c_boost,"A2c",A_2_Aux ,Amod_2c ,0  ,len(A_cost))
        A_2_boost = [sum(values) for values in zip(A_2a_boost,A_2b_boost,A_2c_boost)]

        A_3a_boost = Fill_Boost(A_3a_boost,"A3a",A_3_Aux ,Amod_3a ,0  ,len(A_cost))
        A_3b_boost = Fill_Boost(A_3b_boost,"A3b",A_3_Aux ,Amod_3b ,0  ,len(A_cost))
        A_3c_boost = Fill_Boost(A_3c_boost,"A3c",A_3_Aux ,Amod_3c ,0  ,len(A_cost))
        A_3_boost = [sum(values) for values in zip(A_3a_boost,A_3b_boost,A_3c_boost)]
        print(A_3_boost[29])

        A_4a_boost = Fill_Boost(A_4a_boost,"A4a",A_4_Aux ,Amod_4a ,0  ,len(A_cost))
        A_4b_boost = Fill_Boost(A_4b_boost,"A4b",A_4_Aux ,Amod_4b ,0  ,len(A_cost))
        A_4c_boost = Fill_Boost(A_4c_boost,"A4c",A_4_Aux ,Amod_4c ,0  ,len(A_cost))
        A_4d_boost = Fill_Boost(A_4d_boost,"A4d",A_4_Aux ,Amod_4d ,0  ,len(A_cost))
        A_4_boost = [sum(values) for values in zip(A_4a_boost,A_4b_boost,A_4c_boost,A_4d_boost)]
        print(A_4_boost[29])
        
        B_1_boost = Fill_Boost(B_1_boost,"B",B_1_Aux ,Bmod_1 ,0  ,len(B_cost))
        B_2_boost = Fill_Boost(B_2_boost,"B",B_2_Aux ,Bmod_2 ,0  ,len(B_cost))
        B_3_boost = Fill_Boost(B_3_boost,"B",B_3_Aux ,Bmod_3 ,0  ,len(B_cost))
        B_4_boost = Fill_Boost(B_4_boost,"B",B_4_Aux ,Bmod_4 ,0  ,len(B_cost))
        C_1_boost = Fill_Boost(C_1_boost,"C",C_1_Aux ,Damage_Distribution['C_1']    ,0  ,len(C_cost))

        print('A_1 Base :' + str(round(Amod_1,5)))
        print('A_2a Base :' + str(round(Amod_2a,5)))
        print('A_2b Base :' + str(round(Amod_2b,5)))
        print('A_2c Base :' + str(round(Amod_2c,5)))
        print('A_3a Base :' + str(round(Amod_3a,5)))
        print('A_3b Base :' + str(round(Amod_3b,5)))
        print('A_3c Base :' + str(round(Amod_3c,5)))
        print('A_4a Base :' + str(round(Amod_4a,5)))
        print('A_4b Base :' + str(round(Amod_4b,5)))
        print('A_4c Base :' + str(round(Amod_4c,5)))
        print('A_4d Base :' + str(round(Amod_4d,5)))
        print('B_1 Base :' + str(round(Bmod_1,5)))
        print('B_2 Base :' + str(round(Bmod_2,5)))
        print('B_3 Base :' + str(round(Bmod_3,5)))
        print('B_4 Base :' + str(round(Bmod_4,5)))
        print('C_1 Base :' + str(round(C_1,5)))

#        for i in range(len(C_1_boost)):
#            print(C_1_boost[i])

    # input initial boost and cost values
    if Level_Distribution['A_1_Level'] != 0:
        BoostArray['A_1'] = A_1_boost[Level_Distribution['A_1_Level']-1]
    if Level_Distribution['A_2_Level'] != 0:
        BoostArray['A_2'] = A_2_boost[Level_Distribution['A_2_Level']-1]
    if Level_Distribution['A_3_Level'] != 0:
        BoostArray['A_3'] = A_3_boost[Level_Distribution['A_3_Level']-1]
    if Level_Distribution['A_4_Level'] != 0:
        BoostArray['A_4'] = A_4_boost[Level_Distribution['A_4_Level']-1]
    if Level_Distribution['B_1_Level'] != 0:
        BoostArray['B_1'] = B_1_boost[Level_Distribution['B_1_Level']-1]
    if Level_Distribution['B_2_Level'] != 0:
        BoostArray['B_2'] = B_2_boost[Level_Distribution['B_2_Level']-1]
    if Level_Distribution['B_3_Level'] != 0:
        BoostArray['B_3'] = B_3_boost[Level_Distribution['B_3_Level']-1]
    if Level_Distribution['B_4_Level'] != 0:
        BoostArray['B_4'] = B_4_boost[Level_Distribution['B_4_Level']-1]
    if Level_Distribution['C_1_Level'] != 0:
        BoostArray['C_1'] = C_1_boost[Level_Distribution['C_1_Level']-1]
    else:
        BoostArray['C_1'] = C_1
        
    if Level_Distribution['A_1_Level'] != 0:
        CostArray['A_1'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_1_Level'] - 1)
    if Level_Distribution['A_2_Level'] != 0:
        CostArray['A_2'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_2_Level'] - 1)
    if Level_Distribution['A_3_Level'] != 0:
        CostArray['A_3'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_3_Level'] - 1)
    if Level_Distribution['A_4_Level'] != 0:
        CostArray['A_4'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_4_Level'] - 1)
    if Level_Distribution['B_1_Level'] != 0:
        CostArray['B_1'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_1_Level'] - 1)
    if Level_Distribution['B_2_Level'] != 0:
        CostArray['B_2'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_2_Level'] - 1)
    if Level_Distribution['B_3_Level'] != 0:
        CostArray['B_3'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_3_Level'] - 1)
    if Level_Distribution['B_4_Level'] != 0:
        CostArray['B_4'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_4_Level'] - 1)
    if Level_Distribution['C_1_Level'] != 0:
        CostArray['C_1'] = sum_entries_up_to_number(C_cost,Level_Distribution['C_1_Level'] - 1)
    else:
        CostArray['C_1'] = 0

    if C_1_Changed == False:
        print('Total FD gain at the start : ' + str(round(sum(BoostArray.values()),5)))
    else:
        print('Total FD gained currently : ' + str(round(sum(BoostArray.values()),5) - Damage_Distribution['C_1']))
    print('Total Resources Spent     : ' + str(round(sum(CostArray.values()),0)))
    print('')

    if Toggle_Stuff['ForceMasteryA1234']:
        PassCount = 0
        First_A_1 = 0
        First_A_2 = 0
        First_A_3 = 0
        First_A_4 = 0
    
    # print(Amod_1,Bmod_1,Bmod_2,Bmod_3,Bmod_4,C_1)
    while Level_Distribution['A_1_Level'] != 30 or Level_Distribution['A_2_Level'] != 30 or Level_Distribution['B_1_Level'] != 30 or Level_Distribution['B_2_Level'] != 30 or Level_Distribution['B_3_Level'] != 30 or Level_Distribution['B_4_Level'] != 30 or Level_Distribution['C_1_Level'] != 30:
        A_1_Delta_boost = ListSubtractConstant(A_1_boost,Level_Distribution['A_1_Level'])
        A_2_Delta_boost = ListSubtractConstant(A_2_boost,Level_Distribution['A_2_Level'])
        A_3_Delta_boost = ListSubtractConstant(A_3_boost,Level_Distribution['A_3_Level'])
        A_4_Delta_boost = ListSubtractConstant(A_4_boost,Level_Distribution['A_4_Level'])
        B_1_Delta_boost = ListSubtractConstant(B_1_boost,Level_Distribution['B_1_Level'])
        B_2_Delta_boost = ListSubtractConstant(B_2_boost,Level_Distribution['B_2_Level'])
        B_3_Delta_boost = ListSubtractConstant(B_3_boost,Level_Distribution['B_3_Level'])
        B_4_Delta_boost = ListSubtractConstant(B_4_boost,Level_Distribution['B_4_Level'])
        C_1_Delta_boost = ListSubtractConstant(C_1_boost,Level_Distribution['C_1_Level'])
    #    print("Delta_Boost")
    #    ListPrint(B_3_Delta_boost)

        A_1_Tcost = Fill_Costs(A_cost,Level_Distribution['A_1_Level'])
        A_2_Tcost = Fill_Costs(A_cost,Level_Distribution['A_2_Level'])
        A_3_Tcost = Fill_Costs(A_cost,Level_Distribution['A_3_Level'])
        A_4_Tcost = Fill_Costs(A_cost,Level_Distribution['A_4_Level'])
        B_1_Tcost = Fill_Costs(B_cost,Level_Distribution['B_1_Level'])
        B_2_Tcost = Fill_Costs(B_cost,Level_Distribution['B_2_Level'])
        B_3_Tcost = Fill_Costs(B_cost,Level_Distribution['B_3_Level'])
        B_4_Tcost = Fill_Costs(B_cost,Level_Distribution['B_4_Level'])
        C_1_Tcost = Fill_Costs(C_cost,Level_Distribution['C_1_Level'])
    #    print("TCost")
    #    ListPrint(C_1_Tcost)

        # divide FD gain over costs
        A_1_BoostOverCost = ListByListDivide(A_1_Delta_boost, A_1_Tcost)
        A_2_BoostOverCost = ListByListDivide(A_2_Delta_boost, A_2_Tcost)
        A_3_BoostOverCost = ListByListDivide(A_3_Delta_boost, A_3_Tcost)
        A_4_BoostOverCost = ListByListDivide(A_4_Delta_boost, A_4_Tcost)
        B_1_BoostOverCost = ListByListDivide(B_1_Delta_boost, B_1_Tcost)
        B_2_BoostOverCost = ListByListDivide(B_2_Delta_boost, B_2_Tcost)
        B_3_BoostOverCost = ListByListDivide(B_3_Delta_boost, B_3_Tcost)
        B_4_BoostOverCost = ListByListDivide(B_4_Delta_boost, B_4_Tcost)
        C_1_BoostOverCost = ListByListDivide(C_1_Delta_boost, C_1_Tcost)

    #    print("DeltaBoost/Cost")
    #    ListPrint(C_1_BoostOverCost)
        # add some ID tags to the lists
        A_1_BoostOverCost = [[i + 1, val, "A_1"] for i, val in enumerate(A_1_BoostOverCost)]
        A_2_BoostOverCost = [[i + 1, val, "A_2"] for i, val in enumerate(A_2_BoostOverCost)]
        A_3_BoostOverCost = [[i + 1, val, "A_3"] for i, val in enumerate(A_3_BoostOverCost)]
        A_4_BoostOverCost = [[i + 1, val, "A_4"] for i, val in enumerate(A_4_BoostOverCost)]
        B_1_BoostOverCost = [[i + 1, val, "B_1"] for i, val in enumerate(B_1_BoostOverCost)]
        B_2_BoostOverCost = [[i + 1, val, "B_2"] for i, val in enumerate(B_2_BoostOverCost)]
        B_3_BoostOverCost = [[i + 1, val, "B_3"] for i, val in enumerate(B_3_BoostOverCost)]
        B_4_BoostOverCost = [[i + 1, val, "B_4"] for i, val in enumerate(B_4_BoostOverCost)]
        C_1_BoostOverCost = [[i + 1, val, "C_1"] for i, val in enumerate(C_1_BoostOverCost)]

        if Toggle_Stuff['ForceMasteryA1234'] == True:
            if PassCount == 0:
                for i in range(len(A_1_BoostOverCost)):
                    if A_1_BoostOverCost[i][0] == 1:
                        First_A_1 = i
                        A_1_BoostOverCost.insert(0,A_1_BoostOverCost[First_A_1])
                        A_1_BoostOverCost[0][1] = 1000
                        del A_1_BoostOverCost[First_A_1+1]
                        PassCount += 1
                        break
            elif PassCount == 1:
                for i in range(len(A_2_BoostOverCost)):
                    if A_2_BoostOverCost[i][0] == 1:
                        First_A_2 = i
                        A_2_BoostOverCost.insert(0,A_2_BoostOverCost[First_A_2])
                        A_2_BoostOverCost[0][1] = 1000
                        del A_2_BoostOverCost[First_A_2+1]
                        PassCount += 1
                        break
            elif PassCount == 2:
                for i in range(len(A_3_BoostOverCost)):
                    if A_3_BoostOverCost[i][0] == 1:
                        First_A_3 = i
                        A_3_BoostOverCost.insert(0,A_3_BoostOverCost[First_A_3])
                        A_3_BoostOverCost[0][1] = 1000
                        del A_3_BoostOverCost[First_A_3+1]
                        PassCount += 1
                        break
            elif PassCount == 3:
                for i in range(len(A_4_BoostOverCost)):
                    if A_4_BoostOverCost[i][0] == 1:
                        First_A_4 = i
                        A_4_BoostOverCost.insert(0,A_4_BoostOverCost[First_A_4])
                        A_4_BoostOverCost[0][1] = 1000
                        del A_4_BoostOverCost[First_A_4+1]
                        PassCount += 1
                        break
            
        # sort in descending order for total damage / cost    
        A_1_BoostOverCost = sorted(A_1_BoostOverCost, key=lambda x: x[1], reverse = True)
        A_2_BoostOverCost = sorted(A_2_BoostOverCost, key=lambda x: x[1], reverse = True)
        A_3_BoostOverCost = sorted(A_3_BoostOverCost, key=lambda x: x[1], reverse = True)
        A_4_BoostOverCost = sorted(A_4_BoostOverCost, key=lambda x: x[1], reverse = True)
        B_1_BoostOverCost = sorted(B_1_BoostOverCost, key=lambda x: x[1], reverse = True)
        B_2_BoostOverCost = sorted(B_2_BoostOverCost, key=lambda x: x[1], reverse = True)
        B_3_BoostOverCost = sorted(B_3_BoostOverCost, key=lambda x: x[1], reverse = True)
        B_4_BoostOverCost = sorted(B_4_BoostOverCost, key=lambda x: x[1], reverse = True)
        C_1_BoostOverCost = sorted(C_1_BoostOverCost, key=lambda x: x[1], reverse = True)

        A_1_BoostOverCost_Filtered = SequentialFilter(A_1_BoostOverCost)
        A_2_BoostOverCost_Filtered = SequentialFilter(A_2_BoostOverCost)
        A_3_BoostOverCost_Filtered = SequentialFilter(A_3_BoostOverCost)
        A_4_BoostOverCost_Filtered = SequentialFilter(A_4_BoostOverCost)
        B_1_BoostOverCost_Filtered = SequentialFilter(B_1_BoostOverCost)
        B_2_BoostOverCost_Filtered = SequentialFilter(B_2_BoostOverCost)
        B_3_BoostOverCost_Filtered = SequentialFilter(B_3_BoostOverCost)
        B_4_BoostOverCost_Filtered = SequentialFilter(B_4_BoostOverCost)
        C_1_BoostOverCost_Filtered = SequentialFilter(C_1_BoostOverCost)

        # fuse all the lists
        MegaList = A_1_BoostOverCost_Filtered + A_2_BoostOverCost_Filtered + A_3_BoostOverCost_Filtered + A_4_BoostOverCost_Filtered + B_1_BoostOverCost_Filtered + B_2_BoostOverCost_Filtered + B_3_BoostOverCost_Filtered + B_4_BoostOverCost_Filtered +  C_1_BoostOverCost_Filtered
        # sort by efficiency
        MegaList = sorted(MegaList, key=lambda x: x[1], reverse = True)
        #ListPrint(MegaList)
        #print('')
            
        # The first entry on the compressed list is a single entry, record the level changes, repeat the process, until everything is level 30
        if MegaList[0][2]   == "A_1":
            Level_Distribution['A_1_Level'] = MegaList[0][0]
            BoostArray['A_1'] = A_1_boost[Level_Distribution['A_1_Level'] - 1]
            CostArray['A_1'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_1_Level'] - 1)
        elif MegaList[0][2] == "A_2":
            Level_Distribution['A_2_Level'] = MegaList[0][0]
            BoostArray['A_2'] = A_2_boost[Level_Distribution['A_2_Level'] - 1]
            CostArray['A_2'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_2_Level'] - 1)
        elif MegaList[0][2] == "A_3":
            Level_Distribution['A_3_Level'] = MegaList[0][0]
            BoostArray['A_3'] = A_3_boost[Level_Distribution['A_3_Level'] - 1]
            CostArray['A_3'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_3_Level'] - 1)
        elif MegaList[0][2] == "A_4":
            Level_Distribution['A_4_Level'] = MegaList[0][0]
            BoostArray['A_4'] = A_4_boost[Level_Distribution['A_4_Level'] - 1]
            CostArray['A_4'] = sum_entries_up_to_number(A_cost,Level_Distribution['A_4_Level'] - 1)
        elif MegaList[0][2] == "B_1":
            Level_Distribution['B_1_Level'] = MegaList[0][0]
            BoostArray['B_1'] = B_1_boost[Level_Distribution['B_1_Level'] - 1]
            CostArray['B_1'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_1_Level'] - 1)
        elif MegaList[0][2] == "B_2":
            Level_Distribution['B_2_Level'] = MegaList[0][0]
            BoostArray['B_2'] = B_2_boost[Level_Distribution['B_2_Level'] - 1]
            CostArray['B_2'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_2_Level'] - 1)
        elif MegaList[0][2] == "B_3":
            Level_Distribution['B_3_Level'] = MegaList[0][0]
            BoostArray['B_3'] = B_3_boost[Level_Distribution['B_3_Level'] - 1]
            CostArray['B_3'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_3_Level'] - 1)
        elif MegaList[0][2] == "B_4":
            Level_Distribution['B_4_Level'] = MegaList[0][0]
            BoostArray['B_4'] = B_4_boost[Level_Distribution['B_4_Level'] - 1]
            CostArray['B_4'] = sum_entries_up_to_number(B_cost,Level_Distribution['B_4_Level'] - 1)
        elif MegaList[0][2] == "C_1":
            Level_Distribution['C_1_Level'] = MegaList[0][0]
            BoostArray['C_1'] = C_1_boost[Level_Distribution['C_1_Level'] - 1]
            CostArray['C_1'] = sum_entries_up_to_number(C_cost,Level_Distribution['C_1_Level'] - 1)
            
        BoostArraySum = round(sum(BoostArray.values()),5)
        CostArraySum = round(sum(CostArray.values()))
        MegaList[0].append(BoostArraySum)
        MegaList[0].append(CostArraySum)
        Final_List.append(MegaList[0])
        
    if Toggle_Stuff['Hexa_Stat_Include'] == True:
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
            'Damage'        : Base_Numbers['Damage'],
            'Ignore Def'    : Base_Numbers['IED'],
            'Crit Damage'   : Additional_Numbers['Crit_Dmg'],
            'Attack'        : Additional_Numbers['Att_Power'] / (1 + Additional_Numbers['Att_Perc']),
            'Stat'          : Additional_Numbers['Stat']
        }

        # print(Stat_dict)
        #               0     1     2     3     4     5     6     7     8     9    10
        Stat_Costs = [10.0, 10.0, 10.0, 20.0, 20.0, 20.0, 20.0, 30.0, 40.0, 50.0, 50.0]
        Main_Prob  = [0.35, 0.35, 0.35, 0.20, 0.20, 0.20, 0.20, 0.15, 0.10, 0.05, 0.00]
        #               0     1     2     3     4     5     6     7     8     9     10
        Main_Multi = [0.00, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.65, 0.80, 1.00]
        Alt_Multi  = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

        if Toggle_Stuff['Hexa_Maxed'] == True:
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
            Stat_dict[Stat_dict_tag_Main] = GiveMeCleanValues(True,Stat_Values,Main_Multi,Alt_Multi,Stat_dict.get(Stat_dict_tag_Main),Hexa_Stat_Main[0],Hexa_Stat_Main[1])
            Stat_dict[Stat_dict_tag_Alt_0] = GiveMeCleanValues(False,Stat_Values,Main_Multi,Alt_Multi,Stat_dict.get(Stat_dict_tag_Alt_0),Hexa_Stat_Alt_0[0],Hexa_Stat_Alt_0[1])
            Stat_dict[Stat_dict_tag_Alt_1] = GiveMeCleanValues(False,Stat_Values,Main_Multi,Alt_Multi,Stat_dict.get(Stat_dict_tag_Alt_1),Hexa_Stat_Alt_1[0],Hexa_Stat_Alt_1[1])

        # print(Stat_dict)
        Crit_Main_Mod = (Stat_Values['Crit Damage'] + 1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2) / (1 + Stat_dict['Crit Damage'] + (0.2 + 0.5)/2)
        Boss_Main_Mod = (Stat_Values['Boss Damage'] + Stat_dict['Damage'] + 1) / (Stat_dict['Damage'] + 1)
        IED_Main_Mod  = (1-Base_Numbers['Boss_Def']*(1-Stat_dict['Ignore Def'])*(1-Base_Numbers['Hidden_IED'])*(1-Stat_Values['Ignore Def']))/(1-Base_Numbers['Boss_Def']*(1-Stat_dict['Ignore Def'])*(1-Base_Numbers['Hidden_IED']))
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
            IED_Main_Mod  =((Stat_Values['Ignore Def'] * Multi_mod - 1)*Base_Numbers['Boss_Def']*(1-Stat_dict['Ignore Def'])*(1-Base_Numbers['Hidden_IED'])+1) / (1-Base_Numbers['Boss_Def']*(1-Stat_dict['Ignore Def'])*(1-Base_Numbers['Hidden_IED']))
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
            IED_Main_Mod  =((Stat_Values['Ignore Def'] * Multi_mod - 1)*Base_Numbers['Boss_Def']*(1-Stat_dict['Ignore Def'])*(1-Base_Numbers['Hidden_IED'])+1) / (1-Base_Numbers['Boss_Def']*(1-Stat_dict['Ignore Def'])*(1-Base_Numbers['Hidden_IED']))
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
        if Toggle_Stuff['Hexa_Maxed'] == False:
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
            
    def format_scientific_notation(lst):
        return [lst[0], format(lst[1], '.5e'), *lst[2:]]

    # Apply the formatting to each sublist
    Compressed_Final_List = [format_scientific_notation(sublist) for sublist in Compressed_Final_List]

    #    print("next")
    ListPrint(Compressed_Final_List)
    # printing stuff

    grid_width, grid_height = 12, 4  # You can adjust these dimensions as needed
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
    image_A_2 = Image.open(os.path.join(current_directory, "A_2.png"))
    image_A_3 = Image.open(os.path.join(current_directory, "A_3.png"))
    image_A_4 = Image.open(os.path.join(current_directory, "A_4.png"))
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

    if Toggle_Stuff['Frag_Base'] == True:
        supplementary_title = "(Fragments)"
    else:
        supplementary_title = "(Energy)"
        
    title_text = "Dark Knight 6th Job Optimization GMS " + supplementary_title 
    author_text = "By: LazyVista (XseedGames)"
    if Toggle_Stuff['Hexa_Stat_Include'] == True:
        if Toggle_Stuff['Hexa_Maxed'] == False:
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
    if Toggle_Stuff['Hexa_Stat_Include'] == True:
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
            elif Compressed_Final_List[entry][2] == "A_2":
                canvas.paste(image_A_2.resize((image_size, image_size)), (x, y))
            elif Compressed_Final_List[entry][2] == "A_3":
                canvas.paste(image_A_3.resize((image_size, image_size)), (x, y))
            elif Compressed_Final_List[entry][2] == "A_4":
                canvas.paste(image_A_4.resize((image_size, image_size)), (x, y))
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

First_Run = True

def create_dict_gui(dictionaries, bool_vars):
    global First_Run

    def update_all():
        for var_name, checkbox_var in checkbox_vars.items():
            bool_vars[var_name] = checkbox_var.get()

        for dictionary, entry_widgets in zip(dictionaries, entry_widgets_list):
            for key, entry in entry_widgets.items():
                new_value = entry.get()
                try:
                    # Try to convert the input to the appropriate data type
                    new_value = eval(new_value)
                except:
                    pass
                dictionary[key] = new_value
        update_display()
        Run_Main()
        
    def update_display():
        # Clear the current display
        for widget in frame.winfo_children():
            widget.destroy()

        # Display checkboxes for boolean variables at the top
        checkbox_vars.clear()
        for i, (var_name, var_value) in enumerate(bool_vars.items()):
            bool_var = tk.BooleanVar(value=var_value)
            checkbox = tk.Checkbutton(frame, text=var_name, variable=bool_var)
            checkbox.grid(row=i, column=0, columnspan=2, padx=5, pady=5, sticky='w')
            checkbox_vars[var_name] = bool_var

        # Display the updated dictionaries in a split layout
        for j, (dictionary, entry_widgets) in enumerate(
                zip(dictionaries, entry_widgets_list[-len(dictionaries):])):
            keys_frame = tk.Frame(frame)
            keys_frame.grid(row=j + len(bool_vars), column=0, padx=5, pady=5, sticky='e')

            values_frame = tk.Frame(frame)
            values_frame.grid(row=j + len(bool_vars), column=1, padx=5, pady=5, sticky='w')

            for k, (key, value) in enumerate(dictionary.items()):
                label = tk.Label(keys_frame, text=f"{key}:")
                label.grid(row=k, column=0, padx=5, pady=5, sticky='e')

                entry = tk.Entry(values_frame, width=10)  # Set the width here
                entry.insert(tk.END, str(value))
                entry.grid(row=k, column=0, padx=5, pady=5, sticky='w')

                entry_widgets[key] = entry
                entry_widgets_list[dictionaries.index(dictionary)] = entry_widgets

        # Add "Update All" button at the bottom
        update_all_button = tk.Button(frame, text="Update All", command=update_all)
        update_all_button.grid(row=j + len(bool_vars) + 1, column=0, columnspan=2, padx=5, pady=10)

    # Create a frame to hold the widgets
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    entry_widgets_list = [{key: None for key in dictionary.keys()} for dictionary in dictionaries]
    checkbox_vars = {}

    # Display the initial dictionaries
    if First_Run:
        update_display()
        First_Run = False

# Create the main window
root = tk.Tk()
root.title("Dictionary GUI")

# Run the GUI
create_dict_gui([Base_Numbers, Damage_Distribution, Level_Distribution, Additional_Numbers], Toggle_Stuff)
Run_Main()

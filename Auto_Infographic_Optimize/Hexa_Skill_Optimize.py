from PIL import Image, ImageDraw, ImageFont
import numpy

## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
## VERY IMPORTANT TO FILL BOXES (DAMAGE, IED, BOSS_DEF, A_1 ..... C_1_Current)
# Damage is Boss% + Damage%,
# IED is what you see on character sheet
# if you dont know what Boss_Def is this calc is way too advanced for you
# Use fractional values 98% = 0.98, 612% = 6.12, etc etc
Damage  = 6.00
IED     = 0.94
Boss_Def= 3.80

# Before Origin BA values (use fraction values 0.25, 0.5, 0.1, etc etc)
# A_1 represents the BA contribute of your 4th job skill that is boosted
# B_1 means your first 5th job skill (Spear for ex),B_2 for the second 5th job skill (Radiant Evil)
# B_3 for third (Cyclone), etc etc
# C_1 represents your Origin Skill, and how big you expect it to be (BA percentage wise)
# Input an estimated BA contribution for level one if Origin is currently unleveled
A_1     = 0.25
B_1     = 0.25
B_2     = 0.2
B_3     = 0.15
B_4     = 0.08
C_1     = 0.12

# Current Skill Levels (6th Core)
A_1_Current   = 0
B_1_Current   = 0
B_2_Current   = 0
B_3_Current   = 0
B_4_Current   = 0
C_1_Current   = 0

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
            List[i]     = ((240+5*(i+1))/225 * Aux - 1) * Val
        elif ID == "B":
            Aux         = 1
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
                Aux     = 1
                List[i] = C_1 + round((i) * Aux * Val/30,sig_fig)
            elif (i+1) < 20:
                Aux     = (1-Boss_Def*(1-IED)*(1-.2))/(1-Boss_Def*(1-IED))
                List[i] = C_1 + round((i) * Aux * Val/30,sig_fig)
            elif (i+1) < 30:
                Aux     = (1-Boss_Def*(1-IED)*(1-.2))/(1-Boss_Def*(1-IED)) * (1 + Damage + .2) / (1 + Damage)
                List[i] = C_1 + round((i) * Aux * Val/30,sig_fig)
            elif (i+1) == 30:
                Aux     = (1-Boss_Def*(1-IED)*(1-.2)*(1-0.3))/(1-Boss_Def*(1-IED)) * (1 + Damage + .2 + .3) / (1 + Damage)
                List[i] = C_1 + round((i) * Aux * Val/30,sig_fig)
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
    Bmod_2  = Revert_Bmod_1 * ( 1 + Delta_T )
    Bmod_3  = Revert_Bmod_1 * ( 1 + Delta_T )
    Bmod_4  = Revert_Bmod_1 * ( 1 + Delta_T )
    C_1     = Revert_C_1 * ( 1 + Delta_T )
    
    A_1_boost = Fill_Boost(A_1_boost,"A",A_1_Aux ,Amod_1 ,0  ,len(A_cost))
    B_1_boost = Fill_Boost(B_1_boost,"B",B_1_Aux ,Bmod_1 ,0  ,len(B_cost))
    B_2_boost = Fill_Boost(B_2_boost,"B",B_2_Aux ,Bmod_2 ,0  ,len(B_cost))
    B_3_boost = Fill_Boost(B_3_boost,"B",B_3_Aux ,Bmod_3 ,0  ,len(B_cost))
    B_4_boost = Fill_Boost(B_4_boost,"B",B_4_Aux ,Bmod_4 ,0  ,len(B_cost))
    C_1_boost = Fill_Boost(C_1_boost,"C",C_1_Aux ,C_1    ,0  ,len(C_cost))

while A_1_Current != 30 or B_1_Current != 30 or B_2_Current != 30 or B_3_Current != 30 or B_4_Current != 30 or C_1_Current != 30:
    A_1_Delta_boost = ListSubtractConstant(A_1_boost,A_1_Current)
    B_1_Delta_boost = ListSubtractConstant(B_1_boost,B_1_Current)
    B_2_Delta_boost = ListSubtractConstant(B_2_boost,B_2_Current)
    B_3_Delta_boost = ListSubtractConstant(B_3_boost,B_3_Current)
    B_4_Delta_boost = ListSubtractConstant(B_4_boost,B_4_Current)
    C_1_Delta_boost = ListSubtractConstant(C_1_boost,C_1_Current)
#    print("Delta_Boost")
#    ListPrint(C_1_Delta_boost)

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

#    print("MegaList")
#    ListPrint(MegaList)
    # merge any consecutive patterns A_1 [0,1,2,3,4,5] -> A_1 [5]
    Compressed_MegaList = [MegaList[0]]  # Initialize with the first element
    for i in range(1, len(MegaList)):
        current_element = MegaList[i]
        previous_element = Compressed_MegaList[-1]

        # Check if the current element's third element is different from the previous one
        if current_element[2] == previous_element[2]:
            Compressed_MegaList[-1] = current_element
        else:
            Compressed_MegaList.append(current_element)
            
    # The first entry on the compressed list is a single entry, record the level changes, repeat the process, until everything is level 30
    if Compressed_MegaList[0][2]   == "A_1":
        A_1_Current = Compressed_MegaList[0][0]
    elif Compressed_MegaList[0][2] == "B_1":
        B_1_Current = Compressed_MegaList[0][0]
    elif Compressed_MegaList[0][2] == "B_2":
        B_2_Current = Compressed_MegaList[0][0]
    elif Compressed_MegaList[0][2] == "B_3":
        B_3_Current = Compressed_MegaList[0][0]
    elif Compressed_MegaList[0][2] == "B_4":
        B_4_Current = Compressed_MegaList[0][0]
    elif Compressed_MegaList[0][2] == "C_1":
        C_1_Current = Compressed_MegaList[0][0]
        
    Final_List.append(Compressed_MegaList[0])
#    print("next")
#    ListPrint(Final_List)
# printing stuff
# Define the canvas size and grid dimensions
canvas_width, canvas_height = 900, 600
grid_width, grid_height = 9, 6  # You can adjust these dimensions as needed
spacing = 20

# Calculate the size of each image and the spacing
image_size = 64  # Adjust the spacing (10) as needed

while len(Final_List) >= grid_width * grid_height:
    grid_height += 1
    canvas_height += image_size + spacing
    
# Load the "Draw.png" file
image_A_1 = Image.open("A_1.png")
image_B_1 = Image.open("B_1.png")
image_B_2 = Image.open("B_2.png")
image_B_3 = Image.open("B_3.png")
image_B_4 = Image.open("B_4.png")
image_C_1 = Image.open("C_1.png")

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

title_text = "Dark Knight 6th Job Optimization GMS (Fragment)"
author_text = "By: LazyVista (XseedGames)"
title_font_size = 36  # Adjust to your desired font size
author_font_size = 24  # Adjust to your desired font size
tile_border_size = 2

x_base_shift = 50
y_base_shift = 125

entry = 0

font = ImageFont.truetype("arial.ttf", title_font_size)  # You can change the font family
text_width, text_height = draw.textsize(title_text, font)
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

font = ImageFont.truetype("arial.ttf", author_font_size)  # You can change the font family
text_width, text_height = draw.textsize(author_text, font)
x = (canvas_width - text_width) // 2
y = 80  # You can adjust the Y position for the title
text_position = (x, y)

border_color = (0, 0, 0)  # Black border color
for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
        if dx != 0 or dy != 0:
            border_position = (text_position[0] + dx * border_size, text_position[1] + dy * border_size)
            draw.text(border_position, author_text, fill=border_color, font=font)

draw.text(text_position, author_text, fill=(255, 255, 255), font=font)  # Adjust the text color as needed

for row in range(grid_height):
    for col in range(grid_width):
        x = col * (image_size + spacing) + x_base_shift # Adjust the spacing (10) as needed
        y = row * (image_size + spacing) + y_base_shift # Adjust the spacing (10) as needed

        # Paste the "Draw.png" file into the canvas
        if Final_List[entry][2] == "A_1":
            canvas.paste(image_A_1.resize((image_size, image_size)), (x, y))
        elif Final_List[entry][2] == "B_1":
            canvas.paste(image_B_1.resize((image_size, image_size)), (x, y))
        elif Final_List[entry][2] == "B_2":
            canvas.paste(image_B_2.resize((image_size, image_size)), (x, y))
        elif Final_List[entry][2] == "B_3":
            canvas.paste(image_B_3.resize((image_size, image_size)), (x, y))
        elif Final_List[entry][2] == "B_4":
            canvas.paste(image_B_4.resize((image_size, image_size)), (x, y))
        elif Final_List[entry][2] == "C_1":
            canvas.paste(image_C_1.resize((image_size, image_size)), (x, y))        

        Result_lv = Final_List[entry][0]

        # Calculate the position for the text
        text_position = (x + 15, y + 45)  # Adjust the position as needed

        # Create a font and draw the black border
        font = ImageFont.truetype("arial.ttf", font_size)
        border_color = (0, 0, 0)  # Black border color
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    border_position = (text_position[0] + dx * border_size, text_position[1] + dy * border_size)
                    draw.text(border_position, f"lv. {Result_lv}", fill=border_color, font=font)

        # Draw the text on top of the border
        draw.text(text_position, f"lv. {Result_lv}", fill=(255, 255, 255), font=font)
        
        entry += 1
        if entry == len(Final_List):
            break
    if entry == len(Final_List):
        break

# Save the final canvas image
canvas.save("grid_image_with_text_and_border.png")

# Optionally, display the image
canvas.show()


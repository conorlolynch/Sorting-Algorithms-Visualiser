
import pygame as pg
import numpy as np
import threading
import random
import math
import time
import sys

pg.init()
pg.display.set_caption('Sorting Algorithms')

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_rect = screen.get_rect()
clock = pg.time.Clock()

# Handling all the font stuff
myfont = pg.font.SysFont('didot.ttc', 30, bold=False)

algo_text = myfont.render('Algorithm:', True, (0,0,0))
size_text = myfont.render('Size:', True, (0,0,0))
speed_text = myfont.render('Speed:', True, (0,0,0))


# Some constants for the project
# ------------------------------------------------------------

TASK_BAR_COLOUR = (128,128,128)
BACKGROUND_COLOUR = (180,180,180)

BAR_THICKNESS = 10
BAR_START_X = 1
BAR_START_Y = 30
BAR_SPACE_WIDTH = 0
BAR_MAX_X = SCREEN_WIDTH
BAR_MAX_Y = 500
BAR_COLOUR = (255,69,0)
DRAW_BAR_OUTLINE = True


# Functions for drawing screen and bars
# -------------------------------------------------------------

class Arry():
    def __init__(self, arr, size):
        self.arr = arr
        self.size = size

    def newArry(self, arr):
        self.arr = arr
        self.size = len(arr)

    def getArry(self):
        return self.arr


class RefreshRate():
    def __init__(self, val):
        self.refr = val

    def setRefreshRate(self, val):
        self.refr = val

    def getRefreshRate(self):
        return self.refr


class Button():
    def __init__(self, id, xpos, ypos, length, height, back_colour, highlight_colour, text):
        self.id = id
        self.xpos = xpos
        self.ypos = ypos
        self.length = length
        self.height = height
        self.back_colour = back_colour
        self.highlight_colour = highlight_colour
        self.text = text
        self.font = myfont.render(str(text), True, (0,0,0))
        self.highlight = False


    def changeText(self, text):
        self.text = text
        self.font = myfont.render(str(text), True, (0,0,0))


    def highlightButton(self):
        self.highlight = True


    def unhighlightButton(self):
        self.highlight = False


    def check_collide(self, mouse_x, mouse_y):
        if (mouse_x < self.xpos + self.length and mouse_x > self.xpos):
            if (mouse_y < self.ypos + self.height and mouse_y > self.ypos):
                # Could add click animation?
                return True

        return False


    def draw(self):
        # Draw the main button background
        if (self.highlight):
            pg.draw.rect(screen, self.highlight_colour, (self.xpos, self.ypos, self.length, self.height))
        else:
            pg.draw.rect(screen, self.back_colour, (self.xpos, self.ypos, self.length, self.height))

        # Draw the outline around the button
        pg.draw.rect(screen, (0,0,0), (self.xpos, self.ypos, self.length, self.height), 1)

        # Write the text on the button
        screen.blit(self.font,(self.xpos + 2 , self.ypos + 2))


class DropDownMenu():
    def __init__(self, button_dict):
        # Format --> self.button_dict = { "1: [b1, bubble_sort], 2: [b2, insertion_sort], ... }
        self.button_dict = button_dict
        self.open = False


    def openDrop(self):
        self.open = True


    def closeDrop(self):
        self.open = False


    def checkHover(self, mouse_x, mouse_y):

        # Check all the buttons to see if we have hovered over them
        for button in self.button_dict.values():
            xpos = button[0].xpos
            ypos = button[0].ypos
            l = button[0].length
            h = button[0].height

            if (mouse_x < xpos + l and mouse_x > xpos):
                if (mouse_y < ypos + h and mouse_y > ypos):
                    # Highlight this button
                    button[0].highlightButton()
                else:
                    button[0].unhighlightButton()
            else:
                button[0].unhighlightButton()



    # Check if button was clicked
    def checkClicked(self, mouse_x, mouse_y):

        if (not self.open):
            # Check if mouse x and y are within the top button rectangle
            top_button = self.button_dict.get(1)[0]
            if ((mouse_x < top_button.xpos + top_button.length) and (mouse_x > top_button.xpos)):
                if ((mouse_y < top_button.ypos + top_button.height) and (mouse_y > top_button.ypos)):
                    # Open / close drop down menu
                    self.open = not self.open

        else:
            # Check all the buttons to see if we have clicked one of them
            for button in self.button_dict.values():
                xpos = button[0].xpos
                ypos = button[0].ypos
                l = button[0].length
                h = button[0].height

                if (mouse_x < xpos + l and mouse_x > xpos):
                    if (mouse_y < ypos + h and mouse_y > ypos):
                        # We want to set the name of the algorithm for button 1
                        top_button = self.button_dict.get(1)[0]
                        top_button.changeText(button[0].text)
                        self.open = False

                        # We have clicked this button so run the function associated
                        return self.button_dict.get(button[0].id)[1]

            # If we get this far then we clicked somewhere off screen
            self.open = False
            return None


        return None


    def draw(self):
        if (self.open):
            # Draw all the buttons
            for button in self.button_dict.values():
                button[0].draw()
        else:
            # Just draw the main button
            self.button_dict.get(1)[0].draw()


class Slider():
    def __init__(self, rect_xpos, rect_ypos, rect_length, rect_height, rect_colour, slider_xpos, slider_ypos, slider_radius, slider_colour, min_value, max_value):
        self.rect_xpos = rect_xpos
        self.rect_ypos = rect_ypos
        self.rect_length = rect_length
        self.rect_height = rect_height
        self.rect_colour = rect_colour

        self.slider_xpos = slider_xpos
        self.slider_ypos = slider_ypos
        self.slider_radius = slider_radius
        self.slider_colour = slider_colour
        self.min_value = min_value
        self.max_value = max_value

        self.proportion = self.max_value / self.rect_length
        self.current_value = min_value + (self.proportion * (self.slider_xpos-self.rect_xpos))


    def getSliderValue(self):
        return min_value + (self.proportion * (self.slider_xpos-self.rect_xpos))


    def checkSliderCollided(self, mouse_x, mouse_y):
        # Just figure out if the distance between mouse and centre of circle < radius of circle
        dist = math.sqrt((mouse_x-self.slider_xpos)**2 + (mouse_y-self.slider_ypos)**2)
        if (dist < self.slider_radius):
            return True
        return False


    def set_xpos(self, mouse_x):
        if (mouse_x > self.rect_xpos and mouse_x < self.rect_xpos + self.rect_length):
            self.slider_xpos = mouse_x

    def draw(self):
        # Draw rectangular bit
        pg.draw.rect(screen, self.rect_colour, (self.rect_xpos, self.rect_ypos, self.rect_length, self.rect_height))

        # Draw circular bit
        pg.draw.circle(screen, self.slider_colour, (self.slider_xpos, self.slider_ypos), self.slider_radius, 0)   # Screen, color. center, radius, width



def getNewArray(array_length, min_number, max_number):
    arr = []
    for x in range(array_length):
        arr.append(random.randint(min_number, max_number))

    return arr


def findMaxAndMin(bar_array):
    max = 0
    min = float('inf')
    for num in bar_array:
        if (num > max):
            max = num

        if (num < min):
            min = num

    return max, min


def getScaling(bar_array, max_x, max_y):
    maxy, miny = findMaxAndMin(bar_array)
    scaling_factor = 1

    # So now we see the largest and smallest numbers in the array
    # If the max is bigger than the max limit on screen then we want to scale everything down so it fits
    if (maxy > BAR_MAX_Y):
        scaling_factor = BAR_MAX_Y / max
        return scaling_factor

    # If the max is way less than the limit then we want to scale up closer to this limit to make things look better
    if (maxy < (BAR_MAX_Y / 2)):
        scaling_factor = BAR_MAX_Y / maxy

    return scaling_factor


def getWidthScale(len_array):
    width = (SCREEN_WIDTH - BAR_START_X) / (len_array * BAR_THICKNESS)
    width_by_ten = width * 10
    ans = math.floor(width_by_ten)/10
    return ans


def drawBars(bar_array, start_x, start_y, max_x, max_y, scale_x, width_scale, bool_draw_outline, sorted_index):
    current_x = start_x
    for x, number in enumerate(bar_array):
        # Draw the bars
        if (x < sorted_index):
            pg.draw.rect(screen, (0,255,0), (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (number * scale_x)))
            #pg.draw.rect(screen, (0,255,0), (current_x, BAR_START_Y, BAR_THICKNESS, (number * scale_x)))
        else:
            pg.draw.rect(screen, BAR_COLOUR, (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (number * scale_x)))
            #pg.draw.rect(screen, BAR_COLOUR, (current_x, BAR_START_Y, BAR_THICKNESS, (number * scale_x)))

        # Draw outline around bars
        if (bool_draw_outline and width_scale > 0.3):
            pg.draw.rect(screen, (0, 0, 0), (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (number * scale_x)), 1)  # width = 1
            #pg.draw.rect(screen, (0, 0, 0), (current_x, BAR_START_Y, BAR_THICKNESS, (number * scale_x)), 1)  # width = 1

        # Unhighlight this to see the scaling difference
        #pg.draw.rect(screen, (0, 0, 0), (0, current_y, number, BAR_THICKNESS), 1)  # width = 1
        current_x += int(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH



# Sorting Functions
# -------------------------------------------------------------


# Worst case run time of O(N^2)
def bubble_sort(arr_object, scaling_factor, width_scale, refresh_rate_obj, stop):
    # arr_obj.arr
    arr = arr_object.getArry()
    print("WIDTH SCALE = ",width_scale)

    for i in range(0, len(arr)-1):
        swapped = False

        for x in range(len(arr)-1):

            # This is how we handle terminating this function ran in a thread
            if stop():
                return arr, False

            if (arr[x] > arr[x+1]):
                temp = arr[x+1]
                arr[x+1] = arr[x]
                arr[x] = temp
                swapped = True


            # This is where we handle drawing the bars
            screen.fill(BACKGROUND_COLOUR)
            drawBars(arr, BAR_START_X, BAR_START_Y, BAR_MAX_X, BAR_MAX_Y, scaling_factor, width_scale, DRAW_BAR_OUTLINE, 0)

            # We highlight the bar we are currently on
            current_x = x * ((BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
            pg.draw.rect(screen, (0,255,0), (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[x] * scaling_factor)))

            draw_background()
            drop_down_menu.draw()
            start_button.draw()
            end_button.draw()
            element_number_dropdown.draw()
            slider_button.draw()
            clock.tick(refresh_rate_obj.getRefreshRate())
            pg.display.update()


        # Check if any swaps happened this iteration
        if swapped == False:
            return arr, False

    return arr, False


# Worst case run time of O(N^2)
def insertion_sort(arr_obj, scaling_factor, width_scale, refresh_rate_obj, stop):
    arr = arr_obj.getArry()
    for i in range(1, len(arr)):
        j = i
        while (j > 0 and arr[j-1] > arr[j]):

            # This is how we handle terminating this function ran in a thread
            if stop():
                return arr, False

            temp = arr[j]
            arr[j] = arr[j-1]
            arr[j-1] = temp

            j = j-1

            # This is where we handle drawing the bars
            screen.fill(BACKGROUND_COLOUR)
            drawBars(arr, BAR_START_X, BAR_START_Y, BAR_MAX_X, BAR_MAX_Y, scaling_factor, width_scale, DRAW_BAR_OUTLINE, i)

            # We highlight the i bar
            current_x = i * (math.ceil(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
            pg.draw.rect(screen, (0,0,100), (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[i] * scaling_factor)))

            # We highlight the j bar
            current_x = j * (math.ceil(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
            pg.draw.rect(screen, (128,128,128), (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[j] * scaling_factor)))

            draw_background()
            drop_down_menu.draw()
            start_button.draw()
            end_button.draw()
            element_number_dropdown.draw()
            slider_button.draw()
            clock.tick(refresh_rate_obj.getRefreshRate())
            pg.display.update()

    return arr, False


# Worst case run time of O(N^2)
def selection_sort(arr_obj, scaling_factor, width_scale, refresh_rate_obj, stop):
    arr = arr_obj.getArry()
    j = 0
    n = len(arr)

    while (j < n-1):

        iMin = j
        i = j + 1

        while (i < n):
            # This is how we handle terminating this function ran in a thread
            if stop():
                return arr, False

            if (arr[i] < arr[iMin]):
                iMin = i
            i += 1

            # -------------
            # This is where we handle drawing the bars
            screen.fill(BACKGROUND_COLOUR)
            drawBars(arr, BAR_START_X, BAR_START_Y, BAR_MAX_X, BAR_MAX_Y, scaling_factor, width_scale, DRAW_BAR_OUTLINE, j)


            # We highlight the i bar (The searching bar)
            if (i != len(arr)):
                current_x = i * (math.ceil(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
                pg.draw.rect(screen, (0,255,0), (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[i] * scaling_factor)))

            # We highlight the j bar
            current_x = j * (math.ceil(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
            pg.draw.rect(screen, (0,0,128), (current_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[j] * scaling_factor)))

            draw_background()
            drop_down_menu.draw()
            start_button.draw()
            end_button.draw()
            element_number_dropdown.draw()
            slider_button.draw()
            clock.tick(refresh_rate_obj.getRefreshRate())
            pg.display.update()
            #--------------

        if (iMin != j):
            temp = arr[j]
            arr[j] = arr[iMin]
            arr[iMin] = temp

        j += 1


# Merge sort iterative worst case run time O(nlog(n))
def merge_sort(arr_obj, scaling_factor, width_scale, refresh_rate_obj, stop):
    a = arr_obj.getArry()
    current_size = 1

    # Outer loop for traversing Each
    # sub array of current_size
    while current_size < len(a) - 1:

        left = 0
        while left < len(a)-1:
            mid = min((left + current_size - 1),(len(a)-1))
            right = ((2 * current_size + left - 1,
                    len(a) - 1)[2 * current_size
                        + left - 1 > len(a)-1])

            # Merge call for each sub array
            merge(a, left, mid, right, scaling_factor, width_scale, refresh_rate_obj, stop)

            left = left + current_size*2

        current_size = 2 * current_size


# Merge function for mergesort
def merge(a, l, m, r, scaling_factor, width_scale, refresh_rate_obj, stop):
    n1 = m - l + 1
    n2 = r - m
    L = [0] * n1
    R = [0] * n2

    # This is how we handle terminating this function ran in a thread
    if stop():
        return a, False

    for i in range(0, n1):
        L[i] = a[l + i]
    for i in range(0, n2):
        R[i] = a[m + i + 1]

    i, j, k = 0, 0, l
    while i < n1 and j < n2:

        if L[i] > R[j]:
            a[k] = R[j]
            j += 1
        else:
            a[k] = L[i]
            i += 1
        k += 1

    while i < n1:
        a[k] = L[i]
        i += 1
        k += 1

    while j < n2:
        a[k] = R[j]
        j += 1
        k += 1

    # -------------
    # This is where we handle drawing the bars
    screen.fill(BACKGROUND_COLOUR)
    drawBars(a, BAR_START_X, BAR_START_Y, BAR_MAX_X, BAR_MAX_Y, scaling_factor, width_scale, DRAW_BAR_OUTLINE, 0)


    draw_background()
    drop_down_menu.draw()
    start_button.draw()
    end_button.draw()
    element_number_dropdown.draw()
    slider_button.draw()
    clock.tick(refresh_rate_obj.getRefreshRate())
    pg.display.update()


# Worst case run time of O(N^2)
def quick_sort(arr_obj, scaling_factor, width_scale, refresh_rate, stop):
    arr = arr_obj.getArry()
    l = 0
    h = len(arr)-1

    # Create an auxiliary stack
    size = h - l + 1
    stack = [0] * (size)

    # initialize top of stack
    top = -1

    # push initial values of l and h to stack
    top = top + 1
    stack[top] = l
    top = top + 1
    stack[top] = h

    # Keep popping from stack while is not empty
    while top >= 0:

        # This is how we handle terminating this function ran in a thread
        if stop():
            return arr, False

        # Pop h and l
        h = stack[top]
        top = top - 1
        l = stack[top]
        top = top - 1

        # Set pivot element at its correct position in
        # sorted array
        p = partition( arr, l, h ,scaling_factor, width_scale, refresh_rate, stop)

        # If there are elements on left side of pivot,
        # then push left side to stack
        if p-1 > l:
            top = top + 1
            stack[top] = l
            top = top + 1
            stack[top] = p - 1

        # If there are elements on right side of pivot,
        # then push right side to stack
        if p + 1 < h:
            top = top + 1
            stack[top] = p + 1
            top = top + 1
            stack[top] = h

        # # -------------
        # # This is where we handle drawing the bars
        # screen.fill(BACKGROUND_COLOUR)
        # drawBars(arr, BAR_START_X, BAR_START_Y, BAR_MAX_X, BAR_MAX_Y, scaling_factor, width_scale, DRAW_BAR_OUTLINE, 0)
        #
        # # Highlight the partition bar
        # partition_x = p * (math.ceil(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
        # pg.draw.rect(screen, (0,0,255), (partition_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[p] * scaling_factor)))
        #
        #
        # draw_background()
        # drop_down_menu.draw()
        # start_button.draw()
        # end_button.draw()
        # element_number_dropdown.draw()
        # slider_button.draw()
        # clock.tick(refresh_rate_obj.getRefreshRate())
        # pg.display.update()


# Partition function for quicksort
def partition(arr, l, h, scaling_factor, width_scale, refresh_rate, stop):
    i = ( l - 1 )
    x = arr[h]

    for j in range(l, h):
        if   arr[j] <= x:

            # increment index of smaller element
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

        # -------------
        # This is where we handle drawing the bars
        screen.fill(BACKGROUND_COLOUR)
        drawBars(arr, BAR_START_X, BAR_START_Y, BAR_MAX_X, BAR_MAX_Y, scaling_factor, width_scale, DRAW_BAR_OUTLINE, 0)

        # Highlight the i bar
        partition_x = i * (math.ceil(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
        pg.draw.rect(screen, (0,0,255), (partition_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[i] * scaling_factor)))

        # Highlight the j bar
        partition_x = j * (math.ceil(BAR_THICKNESS * width_scale) + BAR_SPACE_WIDTH)
        pg.draw.rect(screen, (102,0,204), (partition_x, BAR_START_Y, math.ceil(BAR_THICKNESS * width_scale), (arr[j] * scaling_factor)))


        draw_background()
        drop_down_menu.draw()
        start_button.draw()
        end_button.draw()
        element_number_dropdown.draw()
        slider_button.draw()
        clock.tick(refresh_rate_obj.getRefreshRate())
        pg.display.update()

    arr[i + 1], arr[h] = arr[h], arr[i + 1]

    return (i + 1)



def draw_background():
    pg.draw.rect(screen, TASK_BAR_COLOUR, (0, 0, SCREEN_WIDTH, 30))
    # Write the text on taskbar
    screen.blit(algo_text, (40,5))
    screen.blit(size_text, (320,5))
    screen.blit(speed_text, (500,5))




if __name__ == '__main__':
    # Some variables here
    run = True

    # Variables for controling array to be sorted
    arr_length = 50
    min_value = 1
    max_value = 100

    start_array = getNewArray(array_length=arr_length, min_number=min_value, max_number=max_value)
    arr_obj = Arry(start_array, arr_length)
    scaling_factor = getScaling(start_array, BAR_MAX_X, BAR_MAX_Y)
    width_scale = getWidthScale(len(start_array))


    # Drop down menu for changing number of elements
    button_xpos = 380
    button_length = 100
    button_height = 30
    hh_colour = (176,224,230)
    but1 = Button(id = 1, xpos=button_xpos, ypos=0, length=button_length, height=button_height, back_colour=(255,255,0),highlight_colour=hh_colour, text="")
    but2 = Button(id = 2, xpos=button_xpos, ypos=30, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour,text="10")
    but3 = Button(id = 3, xpos=button_xpos, ypos=60, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour,text="50")
    but4 = Button(id = 4, xpos=button_xpos, ypos=90, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour,text="100")
    but5 = Button(id = 5, xpos=button_xpos, ypos=120, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour,text="200")
    but6 = Button(id = 6, xpos=button_xpos, ypos=150, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour,text="400")
    but7 = Button(id = 7, xpos=button_xpos, ypos=180, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour,text="1200")


    button_dict_1 = {1:[but1, None], 2:[but2, 10], 3:[but3, 50], 4:[but4, 100], 5:[but5, 200], 6:[but6, 400], 7:[but7, 1199]}
    element_number_dropdown = DropDownMenu(button_dict_1)


    # Slider for controling speed of algorithm
    rect_xpos = 580
    rect_ypos = 12
    rect_length = 100
    rect_height = 10
    rect_colour = (0,0,0)
    slider_radius = 8
    slider_xpos = rect_xpos + (rect_length//2)
    slider_ypos = rect_ypos + slider_radius//2
    slider_colour = (255,0,0)
    min_value = 30
    max_value = 300
    bool_moving_slider = False

    slider_button = Slider(rect_xpos, rect_ypos, rect_length, rect_height, rect_colour, slider_xpos, slider_ypos, slider_radius, slider_colour, min_value, max_value)


    # Buttons for UI Control
    start_button = Button(id=7, xpos=800, ypos=0, length=50, height=30, back_colour=(0,255,0), highlight_colour=(0,0,255),text="Start")
    end_button = Button(id=8, xpos=900, ypos=0, length=50, height=30, back_colour=(0,255,0), highlight_colour=(0,0,255),text="End")


    # Buttons for the drop down menu
    button_xpos = 150
    button_length = 150
    button_height = 30
    hh_colour = (176,224,230)
    b1 = Button(id = 1, xpos=button_xpos, ypos=0, length=button_length, height=button_height, back_colour=(255,255,0),highlight_colour=hh_colour, text="")
    b2 = Button(id = 2, xpos=button_xpos, ypos=30, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour,text="Bubble Sort")
    b3 = Button(id = 3, xpos=button_xpos, ypos=60, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour, text="Insertion Sort")
    b4 = Button(id = 4, xpos=button_xpos, ypos=90, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour, text="Selection Sort")
    b5 = Button(id = 5, xpos=button_xpos, ypos=120, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour, text="Merge Sort")
    b6 = Button(id = 6, xpos=button_xpos, ypos=150, length=button_length, height=button_height, back_colour=(128,128,128),highlight_colour=hh_colour, text="Quick Sort")


    button_dict = {1:[b1, None], 2:[b2, bubble_sort], 3:[b3, insertion_sort], 4:[b4, selection_sort], 5:[b5, merge_sort], 6:[b6, quick_sort]}
    drop_down_menu = DropDownMenu(button_dict)


    # Control speed of sorting algorithms
    #refresh_rate = 144
    refresh_rate_obj = RefreshRate(slider_button.getSliderValue())

    # Stuff for handling threading
    stop_threads = False
    last_function = None
    t1 = threading.Thread(target = bubble_sort, args =(arr_obj, scaling_factor, width_scale, refresh_rate_obj, lambda : stop_threads, ))

    while run:
        stop_threads = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                stop_threads = True
                if (t1.is_alive()):
                    t1.join()
                sys.exit()

            if event.type == pg.KEYDOWN:
                # Press 's' to start the sorting visualizer
                if event.key == pg.K_s:
                    # Start running the visualizer with the selected sorting algorithm
                    if (not t1.is_alive()):
                        t1.start()


                # Press 'r' to get a new random array to sort
                if event.key == pg.K_r:
                    start_array = getNewArray(array_length=arr_length, min_number=min_value, max_number=max_value)
                    arr_obj.newArry(start_array)
                    scaling_factor = getScaling(start_array, BAR_MAX_X, BAR_MAX_Y)
                    width_scale = getWidthScale(arr_obj.size)
                    print("New array generated")


                # Press 'e' to end the sorting visualizer
                if event.key == pg.K_e:
                    # Use this to stop the current sorting thread?
                    stop_threads = True
                    t1.join()


            # Check if mouse button was clicked
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Get position of mouse click
                    mouse_x, mouse_y = event.pos

                    # Check if we clicked the slider button
                    if(slider_button.checkSliderCollided(mouse_x, mouse_y)):
                        bool_moving_slider = True

                    # Check if we clicked the array size drop down menu
                    size = element_number_dropdown.checkClicked(mouse_x, mouse_y)
                    if (size != None):
                        arr_length = size
                        start_array = getNewArray(array_length=size, min_number=min_value, max_number=max_value)
                        arr_obj.newArry(start_array)
                        scaling_factor = getScaling(start_array, BAR_MAX_X, BAR_MAX_Y)
                        width_scale = getWidthScale(arr_obj.size)

                    # Check if we clicked the algorithm drop down menu
                    func = drop_down_menu.checkClicked(mouse_x, mouse_y)
                    if (func != None):
                        last_function = func
                        #t1 = threading.Thread(target = func, args =(arr_obj, scaling_factor, width_scale, refresh_rate, lambda : stop_threads, ))

                    # Check if we clicked the start button
                    if (start_button.check_collide(mouse_x, mouse_y)):
                        t1 = threading.Thread(target = last_function, args =(arr_obj, scaling_factor, width_scale, refresh_rate_obj, lambda : stop_threads, ))
                        t1.start()
                        #if (not t1.is_alive()):
                        #   t1.start()

                    # Check if we clicked the end button
                    if (end_button.check_collide(mouse_x, mouse_y)):
                        if (t1.is_alive()):
                            stop_threads = True
                            t1.join()

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    bool_moving_slider = False

            if event.type == pg.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                drop_down_menu.checkHover(mouse_x, mouse_y)
                element_number_dropdown.checkHover(mouse_x, mouse_y)

                if (bool_moving_slider):
                    slider_button.set_xpos(mouse_x)
                    refresh_rate_obj.setRefreshRate(slider_button.getSliderValue())



        if (not t1.is_alive()):
            screen.fill(BACKGROUND_COLOUR)
            drawBars(arr_obj.getArry(), BAR_START_X, BAR_START_Y, BAR_MAX_X, BAR_MAX_Y, scaling_factor, width_scale, DRAW_BAR_OUTLINE, 0)
            draw_background()
            drop_down_menu.draw()
            start_button.draw()
            end_button.draw()
            element_number_dropdown.draw()
            slider_button.draw()
            clock.tick(60)
            pg.display.update()

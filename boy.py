# 이것은 각 상태들을 객체로 구현한 것임.

import math
from pico2d import *

def space_down(e):
    return e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_SPACE

def time_out(e):
    return e[0]=='TIME_OUT'

def time_out_5(e):
    return e[0]=='TIME_OUT' and e[1]==5.0

def right_down(e):
    return e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_RIGHT

def right_up(e):
    return e[0]=='INPUT' and e[1].type==SDL_KEYUP and e[1].key==SDLK_RIGHT

def left_down(e):
    return e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_LEFT

def left_up(e):
    return e[0]=='INPUT' and e[1].type==SDL_KEYUP and e[1].key==SDLK_LEFT

def press_a(e):
    return e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_a
class Idle: #기본상태
    @staticmethod
    def do(boy):
        boy.frame=(boy.frame+1)%8
        if get_time()-boy.start_time>3:
            boy.state_machine.handle_event(('TIME_OUT',0))
        pass

    @staticmethod
    def enter(boy,e):
        if boy.action==0:
            boy.action=2
        elif boy.action==1:
            boy.action=3
        boy.dir=0
        boy.start_time=get_time()
        boy.frame=0
        print("Idle enter")
        pass

    @staticmethod
    def exit(boy,e):
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame*100,boy.action*100,100,100,boy.x,boy.y)
        pass
    

class Sleep:

    @staticmethod
    def enter(boy,e):
        boy.frame=0
        print('sleep')
        pass

    @staticmethod
    def exit(boy,e):
        pass

    @staticmethod
    def do(boy):
        boy.frame=(boy.frame+1)%8

    @staticmethod
    def draw(boy):
        if boy.action==2:
            boy.image.clip_composite_draw(boy.frame*100,boy.action*100,100,100,-math.pi/2,' ',boy.x+25,boy.y-25,100,100)
        else:
            boy.image.clip_composite_draw(boy.frame*100,boy.action*100,100,100,math.pi/2,' ',boy.x-25,boy.y-25,100,100)

        pass

class Run:
    @staticmethod
    def enter(boy,e):
        if right_down(e) or left_up(e):
            boy.dir,boy.action=1,1
        elif left_down(e) or right_up(e):
            boy.dir,boy.action=-1,0
        print('run')
    @staticmethod
    def exit(boy,e):
        pass

    @staticmethod
    def do(boy):
        boy.frame=(boy.frame+1)%8
        next_p=boy.x+boy.dir*5
        if(next_p<=800 and next_p>=0):
            boy.x+=boy.dir*5
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame*100,boy.action*100,100,100,boy.x,boy.y)

class AutoRun: #자동이동
    @staticmethod 
    def enter(boy,e): 
        if boy.action==2: #방향에 따른 전환
            boy.dir,boy.action=-1,0
        elif boy.action==3:
            boy.dir,boy.action=1,1
        boy.start_time=get_time()
        print("autorun enter")
        pass

    @staticmethod
    def exit(boy,e):
        pass

    @staticmethod
    def do(boy):
        boy.frame=(boy.frame+1)%8
        if (boy.x+boy.dir*10>=0 and boy.x+boy.dir*10<=800): #default x size
            boy.x+=boy.dir*10
        else :
            boy.action=1 if boy.action==0 else 0
            if boy.dir==1:
                boy.action,boy.dir=0,-1
            elif boy.dir==-1:
                boy.action,boy.dir=1,1
        if get_time()-boy.start_time>3:
            boy.state_machine.handle_event(('TIME_OUT',0))
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame*100,boy.action*100,100,100,boy.x,boy.y+15,150,150)
        pass

class StateMachine:
    def __init__(self,boy):
        self.cur_state = Idle
        self.boy=boy
        self.table={
            Idle:{right_down:Run, left_down:Run, left_up:Run, right_up:Run, time_out:Sleep,press_a:AutoRun},
            Run:{right_down:Idle, left_down:Idle, left_up:Idle, right_up:Idle},
            Sleep:{right_down:Run, left_down:Run, left_up:Run, right_up:Run, space_down:Idle},
            AutoRun:{right_down:Run, left_down:Run, left_up:Run, right_up:Run,time_out:Idle}
            }

    def start(self):
        self.cur_state.enter(self.boy,('START',0))

    def handle_event(self,e):
        for check_evennt, next_state in self.table[self.cur_state].items():
            if check_evennt(e):
                self.cur_state.exit(self.boy,e)
                self.cur_state=next_state
                self.cur_state.enter(self.boy,e)
                return True
        return False

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)




class Boy:
    def __init__(self,name):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT',event))
        pass

    def draw(self):
        self.state_machine.draw()

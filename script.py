import mdl
from display import *
from matrix import *
from draw import *

def pass_one (commands):
    name = ''
    num_frames = 1
    if_frame = False
    if_name = False
    if_vary = False
    for command in commands:
        if command['op'] == 'frames':
            num_frames = int(command['args'][0])
            if_frame = True
        elif command['op'] == 'vary':
            if_vary = True
        elif command['op'] == 'basename':
            name = command['args'][0]
            if_name = True
    if if_vary == True and if_frame == False:
        print('vary: yes, frames: no')
        exit()
    if if_frame == True and if_name == False:
        print('animation: yes, no basename, setting default name')
        name = 'frame'
    return (name, num_frames)

def pass_two (commands, num_frames): 
    frames = [ {} for i in range(num_frames) ]
    for command in commands:
        c = command['op']
        args = command['args']
        if c == 'vary':
            knob = command['knob']
            start_frame = int(args[0])
            end_frame = int(args[1])
            start = args[2]
            end = args[3]
            if start_frame > end_frame:
                exit()
            if end_frame >= num_frames:
                exit()
            value = start
            for i in range(num_frames):
                if i in range(start_frame, end_frame+1):
                    increment = (end-start) / (end_frame-start_frame)
                    frames[i][knob] = value
                    value += increment
    return frames



def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1]
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = pass_one(commands)
    frames = pass_two(commands, num_frames)

    for f in range(num_frames):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []
        if num_frames > 1:
            frame = frames[f]
            for knob in frame:
                symbols[knob][1] = frame[knob]
        for command in commands:
            print(command)
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'mesh':
                if command['constants']:
                    reflect = command['constants'] if command['constants'] != ':' else '.white'
                add_mesh(tmp, command['cs'])
                matrix_mult(stack[-1], tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                if command['knob']:
                    knob_value = symbols[command['knob']][1]
                tmp = make_translate(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if command['knob']:
                    knob_value = symbols[command['knob']][1]
                tmp = make_scale(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if command['knob']:
                    knob_value = symbols[command['knob']][1]
                theta = args[1] * (math.pi/180) * knob_value
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if num_frames > 1:
            print('Saving frame: '  + 'animation/%s%03d'%(name, f))
            save_extension(screen, 'animation/%s%03d'%(name, f))
    if num_frames > 1:
        make_animation(name)
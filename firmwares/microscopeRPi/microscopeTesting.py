from parts import Axis

xAxis = Axis(80,(21,20,16),(26,19),16.0,15)
yAxis = Axis(80,(7,8,25),(13,6),16.0,15)
zAxis = Axis(200,(18,15,14),(11,9),1.0,150)
milimeters = 1

while True:
    print '\n0. Autohome'
    print '1. X Axis forward'
    print '2. X Axis back'
    print '3. Y Axis forward'
    print '4. Y Axis back'
    print '5. Z Axis forward'
    print '6. Z Axis back'
    print '7. Stop all axis'
    print '8. Stop X axis'
    print '9. Stop Y axis'
    print '10. Stop Z axis'
    print '11. Change axis speed'
    print '12. Change milimeters to move'
    print 'Other. EXIT'
    option=input('\nEnter option:')
    if option == 0:
        xAxis.move('back',-1)
        yAxis.move('back',-1)
        zAxis.move('back',-1)
    elif option == 1:
        xAxis.move('forward',milimeters)
    elif option == 2:
        xAxis.move('back',milimeters)
    elif option == 3:
        yAxis.move('forward',milimeters)
    elif option == 4:
        yAxis.move('back',milimeters)
    elif option == 5:
        zAxis.move('forward',milimeters)
    elif option == 6:
        zAxis.move('back',milimeters)
    elif option == 7:
        xAxis.stop()
        yAxis.stop()
        zAxis.stop()
    elif option == 8:
        xAxis.stop()
    elif option == 9:
        yAxis.stop()
    elif option == 10:
        zAxis.stop()
    elif option == 11:
        print '1. X Axis'
        print '2. Y Axis'
        print '3. Z Axis'
        option2 = input('Select axis:')
        newVel = input('Select new speed(rpm):')
        if option2 == 1:
            xAxis.setVelocity(newVel)
        if option2 == 2:
            yAxis.setVelocity(newVel)
        if option2 == 3:
            zAxis.setVelocity(newVel)
    elif option == 12:
       milimeters = input('Select milimeters to move: ')
    else:
        print 'END OF PROGRAM'
        xAxis.stop()
        yAxis.stop()
        zAxis.stop()
        break

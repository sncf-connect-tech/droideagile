from app.DroideAgile import DroideAgile

DroideAgile().run()
# from __future__ import print_function
#
# import time
#
# from app.droid_brick_pi import BrickPiFacadeThread
#
# thread = BrickPiFacadeThread()
#
# thread.ready.subscribe(on_next=lambda x: print(x))
# thread.sensors.subscribe(on_next=lambda x: print("read:" + str(x)))
# thread.buffered_color_sensor_observable.subscribe(on_next=lambda x: print("read:" + str(x)))
#
# time.sleep(10)
# print("stop blablabla")
# thread.stop()
# print("stop blablabla")
#
# thread = BrickPiFacadeThread()
# time.sleep(3)
# thread.stop()

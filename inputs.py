from periphery import I2C

i2c1 = I2C("/dev/i2c-3")  # pins 3/5

print("Success")

while(True):
    print("waiting")

from periphery import I2C

i2c1 = I2C("/dev/i2c-3")  # pins 3/5

msgs = [I2C.Message([0x01, 0x00]), I2C.Message([0x00], read=True)]
i2c1.transfer(0x50, msgs)
print("0x100: 0x{:02x}".format(msgs[1].data[0]))

i2c1.close()
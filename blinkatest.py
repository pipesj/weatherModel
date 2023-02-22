import board
import digitalio
import busio

print("Hello blinka!")
print(dir(board))

# Try to great a Digital input
pin = digitalio.DigitalInOut(board.GPIO13)
print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.I2C1_SCL, board.I2C1_SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SPI_CLK, board.SPI_MI, board.SPI_MO)
print("SPI ok!")

print("done!")
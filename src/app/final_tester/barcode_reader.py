import serial

# Define serial port settings
serial_port = '/dev/ttyACM0'
baud_rate = 9600
byte_size = 8
parity = serial.PARITY_NONE
stop_bits = 1
timeout = 1  # Timeout for reading in seconds

ser = None

try:
    # Create a serial port object
    ser = serial.Serial(
        port=serial_port,
        baudrate=baud_rate,
        bytesize=byte_size,
        parity=parity,
        stopbits=stop_bits,
        timeout=timeout
    )

    # Read and print data from the serial port indefinitely
    while True:
        data = ser.readline().decode('utf-8').strip()  # Assuming data is in UTF-8 encoding
        print("Received:", data)

except serial.SerialException as e:
    print(f"Serial port error: {e}")

except KeyboardInterrupt:
    print("Serial reading stopped.")

finally:
    if ser is not None and ser.is_open:
        ser.close()
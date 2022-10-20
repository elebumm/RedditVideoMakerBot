import datetime

format_data = "%Y-%m-%d %H:%M:%S.%f"
time = datetime.datetime.now().strftime(format_data)
print(time)

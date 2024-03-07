from signal_1 import Signal
from performance import Performance
from data import result_dict,nearest_date_px_last



perf = Performance(result_dict, result_dict)


test = perf.calculate_returns()
print(test[nearest_date_px_last])

print("Hola :)<3")
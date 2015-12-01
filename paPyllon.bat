:: Launch qtlab

cd qtlab
call qtlab.bat
timeout -t 3
cd ..

cd measurement
:: Launch measurement kernel
start Console -w "Measurement console" -r "/k python start_measurement_kernel.py"
:: Launch operator kernel
start Console -w "Operator" -r "/k python start_operator.py"



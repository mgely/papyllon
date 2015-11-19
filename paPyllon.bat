:: Launch qtlab

cd qtlab
call qtlab.bat
timeout -t 3
cd ..

:: Launch measurement kernel
cd measurement
start Console -w "Measurement console" -r "/k python start_kernel.py"
cd ..

:: Launch operator kernel
cd op
start Console -w "Operator" -r "/k python start_kernel.py"
cd ..
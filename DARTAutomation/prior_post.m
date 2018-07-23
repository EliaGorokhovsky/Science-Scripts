diagn_file = 'preassim.nc';
plot_total_err
''
!mv rms_spread_out rms_spread_case
figure(2)
diagn_file = 'analysis.nc';
plot_total_err
''
!cat rms_spread_out >> rms_spread_case
!rm rms_spread_out

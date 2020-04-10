usage:
    start_fitHdf.sh - для него потребуется файл с группами в hdf файле который вы собираетесь использовать
        первый аргумент - файл с данными
        второй аргумент - файл с группами
        третий аргумент - строка с аргументами для fit_data.py 


    fit_data.py
        "filename", type=str
        '-t', '--type', default='npy', help="Type of using datafile. Can be: \'npy\', \'csv\', \'hdf\'"
        '-i', '--istart', default=0, type=int
        '-m', '--mode', default='NexpNtry', type=str
        '-g', '--group', nargs='*', default=[''], help='Which group you want to fit. Need to fit data from hdf'
        '--tcf', default='acf', help='Need to fit data from hdf'
        '-o', '--output', default='out.hdf5', 'filename with ending (npy, hdf5) for saving results'

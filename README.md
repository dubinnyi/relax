## hdreform

   **filename**
   
   **-o**, **--output** default=out - _optimal_
   
   **--tcf**, nargs=*, default=\'\' - _optimal_
   
   **-g**, **--gname**, nargs=*, default=\'\' - _optimal_

   Преобразовывает исходный hdf файл, полученный с помощью impulse. Высчитывает среднее по всем траекториям для указанных групп и типов корреляционных функций. 
   
   Группа tcf в атрибутах хранит group_size и names из исходного файла
   
   Полученный фал имеет следующую структуру: <group_name>/<tcf>/errors -/mean
                                              time

## hdfinfo

   **filename**
   
   **-a**, **--all** - _optimal_, статистика будет выдаваться по каждой группе дополнительно

   Проверяет файл на соответствие структуре файла получаемого с помощью impulse. Выдаёт статистику по файлу: число групп и траекторий, длина трейса и т.д.

## hdfextract

   **filename**
   
   **--tcf** 
   
   **-o**, **--output**, default=out, _optimal_
   
   **-g**, **--gname**,  nargs=*, default=\'\' - _optimal_
   
   **-m**, **--mean** - _optimal_
   
   Извлекает определенную группу (или все) в файл .npy

## fit_data.py

   **filename**
   
   **-t**, **--type**, default=npy, _Type of using datafile. Can be: npy, csv, hdf_
   
   **-i**, **--istart**, default=0
   
   **-m**, **--method**, default=NexpNtry
   
   **-g**, **--group**, nargs=*, default=[\'\'], _Which group you want to fit. Need to fit data from hdf_
   
   **--tcf**, default=acf, _Need to fit data from hdf_
   
   **-o**, **--output**, default=out.hdf5, _filename (npy, hdf5) for saving results_

## dpendencies:

**numpy
scipy
lmfit
h5py
prettytable
pandas**

The utility **hdfview** is usefull for inspection of input/output hdf5 files

The following commands will resolve all recquired dependencies (fedora Linux):
````
 > dnf install -y python3-numpy pythob3-scipy hdfview python3-h5py python3-prettytable python3-pandas
 > pip3 install lmfit
````
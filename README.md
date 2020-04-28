## hdfreform

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

   Input/Output:

   **filename** the input file with `acf/ccf` time series data in `npy`, `csv` or `hdf` format
   
   **-o**, **--output**, default=`out.hdf5`, _filename to output the results_
   
   **-t**, **--type**, data type of input , default=`npy`
   
   In case of `hdf` input file format, the following options will select the data to be fitted:
   
   **-g**, **--group**, nargs=*, default=[\'NH\'], _The group name(s) to fit, multiple groups may be specified
   
   **--tcf**, default=acf, (autocorrelation function), ccf (cross correlation functions) will be supported in the furure 
   
   Method of data fitting:
   
   **-m**, **--method**, default=NexpNtry, reserved for future extensions
   
   Debugging and testing options:
   
   **-i**, **--istart**, default=0. Starts fitting procedure from i-th relaxation group. 
   
### example:
   Fit all `acf` (autocorrelation functions)  of all `NH` groups in file `reformAll.hdf`, 
   write fit results to the file `fit_NH.hdf`:
```
   fit_data.py -t hdf -g NH -o fit_NH.hdf reformAll.hdf
```
  
## dependencies:

**numpy
scipy
lmfit
h5py
prettytable
pandas 
multiprocessing**

The utility **hdfview** is usefull for visualisation of input/output hdf5 files

The following commands will resolve recquired dependencies (fedora Linux):
````
 > dnf install -y python3-numpy python3-scipy hdfview python3-h5py python3-prettytable python3-pandas python3-libs
 > pip3 install lmfit threadpoolctl
````
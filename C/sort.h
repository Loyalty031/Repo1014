/**
 * @file sort.h
 * @author JerryQ
 * @details 一些排序函数
 */

#ifndef MY_SORT_HEADER__NJU_SE_2022__
#define MY_SORT_HEADER__NJU_SE_2022__

#include <stdlib.h>
#include <stdbool.h>

/**
 * @name FROM_SMALL_TO_BIG
 * @category 宏
 * @value true
 * @details 作为参数传递给排序函数，使其对数组从小到大排序
 */
#define FROM_SMALL_TO_BIG true

/**
 * @name FROM_BIG_TO_SMALL
 * @category 宏
 * @value false
 * @details 作为参数传递给排序函数，使其对数组从大到小排序
 */
#define FROM_BIG_TO_SMALL false

/*编译器不是GCC时，去除attribute选项*/
#ifndef __GNUC__
#define __attribute__(...)
#endif  //__GNUC__

/*在C++中使用时，以C的方式调用*/
#ifdef __cplusplus
extern "C" {
#endif  //__cplusplus

/*指定函数的属性和类型*/
#define func(type) __attribute__((__cdecl__, __unused__, __nonnull__(1))) static __inline__ type

/*取最小值*/
#ifndef min
#define min(a, b) (((a) < (b)) ? (a) : (b))
#endif  //min

#ifdef swap
#undef swap
#endif  //swap

/*交换变量的值*/
#define swap(type, a, b)  \
do {                      \
  type temp = (a);        \
  (a) = (b);              \
  (b) = temp;             \
}while (0)

/**
 * @name GenericBubbleSort
 * @param type 需要排序的数组的类型
 * @details 定义type类型的冒泡排序函数
 */
#define GenericBubbleSort(type)                                                 \
func(void) bubbleSort_##type(type arr[], const int len, const bool flag) {      \
  int i, j;                                                                     \
  for (i = 0; i < len - 1; i++) {                                               \
    for (j = 0; j < len - 1 - i; j++) {                                         \
      if ((flag == FROM_SMALL_TO_BIG && arr[j] > arr[j + 1])                    \
      || (flag == FROM_BIG_TO_SMALL && arr[j] < arr[j + 1])) {                  \
        swap(type, arr[j], arr[j + 1]);                                         \
      }                                                                         \
    }                                                                           \
  }                                                                             \
}

/**
 * @name GenericSelectionSort
 * @param type 需要排序的数组的类型
 * @details 定义type类型的选择排序函数
 */
#define GenericSelectionSort(type)                                              \
func(void) selectionSort_##type(type arr[], const int len, const bool flag) {   \
  int i, j;                                                                     \
  for (i = 0; i < len - 1; i++) {                                               \
    int obj = i;                                                                \
    for (j = i + 1; j < len; j++) {                                             \
      if ((flag == FROM_SMALL_TO_BIG && arr[j] < arr[obj])                      \
      || (flag == FROM_BIG_TO_SMALL && arr[j] > arr[obj])) {                    \
        obj = j;                                                                \
      }                                                                         \
    }                                                                           \
    swap(type, arr[obj], arr[i]);                                               \
  }                                                                             \
}

/**
 * @name GenericInsertSort
 * @param type 需要排序的数组的类型
 * @details 定义type类型的插入排序函数
 */
#define GenericInsertSort(type)                                                 \
func(void) insertSort_##type(type arr[], const int len, const bool flag) {      \
  int i;                                                                        \
  for (i = 1; i < len; i++) {                                                   \
    int j = i - 1;                                                              \
    type obj = arr[i];                                                          \
    while (j >= 0 && (flag ? arr[j] > obj : arr[j] < obj)) {                    \
      arr[j + 1] = arr[j];                                                      \
      j--;                                                                      \
    }                                                                           \
    arr[j + 1] = obj;                                                           \
  }                                                                             \
}

/**
 * @name GenericShellSort
 * @param type 需要排序的数组的类型
 * @details 定义type类型的希尔排序函数
 */

#define GenericShellSort(type)                                                  \
func(void) shellSort_##type(type arr[], const int len, const bool flag) {       \
  int gap, i, j;                                                                \
  type temp;                                                                    \
  for (gap = len >> 1; gap > 0; gap >>= 1) {                                    \
    for (i = gap; i < len; i++) {                                               \
      temp = arr[i];                                                            \
      if (flag) {                                                               \
        for (j = i - gap; j >= 0 && arr[j] > temp; j -= gap) {                  \
          arr[j + gap] = arr[j];                                                \
        }                                                                       \
      } else {                                                                  \
        for (j = i - gap; j >= 0 && arr[j] < temp; j -= gap) {                  \
          arr[j + gap] = arr[j];                                                \
        }                                                                       \
      }                                                                         \
      arr[j + gap] = temp;                                                      \
    }                                                                           \
  }                                                                             \
}

/**
 * @name GenericMergeSort
 * @param type 需要排序的数组的类型
 * @details 定义type类型的归并排序函数
 */
#define GenericMergeSort(type)                                                  \
func(void) mergeSort_##type(type arr[], const int len, const bool flag) {       \
  type *arr1 = arr;                                                             \
  type *arr2 = (type*)malloc(len * sizeof(type));                               \
  int seg, start;                                                               \
  for (seg = 1; seg < len; seg *= 2) {                                          \
    for (start = 0; start < len; start += seg * 2) {                            \
      int low = start;                                                          \
      int mid = min(start + seg, len);                                          \
      int high = min(start + seg * 2, len);                                     \
      int k = low;                                                              \
      int start1 = low, end1 = mid;                                             \
      int start2 = mid, end2 = high;                                            \
      while (start1 < end1 && start2 < end2) {                                  \
        if (flag ? arr1[start1] < arr1[start2] : arr1[start1] > arr1[start2]) { \
          arr2[k++] = arr1[start1++];                                           \
        } else {                                                                \
          arr2[k++] = arr1[start2++];                                           \
        }                                                                       \
      }                                                                         \
      while (start1 < end1) {                                                   \
        arr2[k++] = arr1[start1++];                                             \
      }                                                                         \
      while (start2 < end2) {                                                   \
        arr2[k++] = arr1[start2++];                                             \
      }                                                                         \
    }                                                                           \
    swap(type*, arr1, arr2);                                                    \
  }                                                                             \
  if (arr1 != arr) {                                                            \
    int i;                                                                      \
    for (i = 0; i < len; i++) {                                                 \
      arr2[i] = arr1[i];                                                        \
    }                                                                           \
    arr2 = arr1;                                                                \
  }                                                                             \
  free(arr2);                                                                   \
}

/**
 * @name GenericIsUp
 * @param type 需要判断的数组的类型
 * @details 定义判断数组是否为从小到大的函数
 */

#define GenericIsUp(type)                                                       \
func(bool) isUp_##type(const type arr[], const int len) {                       \
  for (int i = 0; i < len - 1; i++){                                            \
    if (arr[i] > arr[i + 1]){                                                   \
      return false;                                                             \
    }                                                                           \
  }                                                                             \
  return true;                                                                  \
}

/**
 * @name GenericIsDown
 * @param type 需要判断的数组的类型
 * @details 定义判断数组是否为从大到小的函数
 */

#define GenericIsDown(type)                                                     \
func(bool) isDown_##type(const type arr[], const int len) {                     \
  for (int i = 0; i < len - 1; i++){                                            \
    if (arr[i] < arr[i + 1]){                                                   \
      return false;                                                             \
    }                                                                           \
  }                                                                             \
  return true;                                                                  \
}


/*预先定义int和double类型的排序函数*/

GenericBubbleSort(int)
GenericBubbleSort(double)

GenericSelectionSort(int)
GenericSelectionSort(double)

GenericInsertSort(int)
GenericInsertSort(double)

GenericShellSort(int)
GenericShellSort(double)

GenericMergeSort(int)
GenericMergeSort(double)

GenericIsUp(int)
GenericIsUp(double)

GenericIsDown(int)
GenericIsDown(double)

/*定义便于使用这些函数的宏*/

/*冒泡排序*/

#ifdef BubbleSort
#undef BubbleSort
#endif

/**
 * @name BubbleSort
 * @category 宏
 * @param arr_type 需要排序的数组的类型
 * @param arr 需要排序的数组
 * @param flag 对数组排序的方式
 * @details 冒泡排序，时间复杂度O(n^2)，空间复杂度O(1)\n
 * 默认对全体数组元素进行排序，如果需要对部分元素排序，请使用原函数\n
 * 除了int和double类型，其他类型应使用GenericBubbleSort宏定义对应的冒泡排序函数
 * @example BubbleSort(int, int_arr, FROM_SMALL_TO_BIG);
 * @sa GenericBubbleSort
 */

#define BubbleSort(arr_type, arr, flag) bubbleSort_##arr_type(arr, sizeof(arr) / sizeof((arr)[0]), flag)

/*选择排序*/

#ifdef SelectionSort
#undef SelectionSort
#endif  //SelectionSort

/**
 * @name SelectionSort
 * @category 宏
 * @param arr_type 需要排序的数组的类型
 * @param arr 需要排序的数组
 * @param flag 对数组排序的方式
 * @details 选择排序，时间复杂度O(n^2)，空间复杂度O(1)\n
 * 默认对全体数组元素进行排序，如果需要对部分元素排序，请使用原函数\n
 * 除了int和double类型，其他类型应使用GenericSelectionSort宏定义对应的选择排序函数
 * @example SelectionSort(int, int_arr, FROM_SMALL_TO_BIG);
 * @sa GenericSelectionSort
 */

#define SelectionSort(arr_type, arr, flag) selectionSort_##arr_type(arr, sizeof(arr) / sizeof((arr)[0]), flag)

/*插入排序*/

#ifdef InsertSort
#undef InsertSort
#endif  //InsertSort

/**
 * @name InsertSort
 * @category 宏
 * @param arr_type 需要排序的数组的类型
 * @param arr 需要排序的数组
 * @param flag 对数组排序的方式
 * @details 插入排序，时间复杂度O(n^2)，空间复杂度O(1)\n
 * 默认对全体数组元素进行排序，如果需要对部分元素排序，请使用原函数\n
 * 除了int和double类型，其他类型应使用GenericInsertSort宏定义对应的插入排序函数
 * @example InsertSort(int, int_arr, FROM_SMALL_TO_BIG);
 * @sa GenericInsertSort
 */

#define InsertSort(arr_type, arr, flag) insertSort_##arr_type(arr, sizeof(arr) / sizeof((arr)[0]), flag)

/*希尔排序*/

#ifdef ShellSort
#undef ShellSort
#endif  //ShellSort

/**
 * @name ShellSort
 * @category 宏
 * @param arr_type 需要排序的数组的类型
 * @param arr 需要排序的数组
 * @param flag 对数组排序的方式
 * @details 希尔排序，时间复杂度O(n log(n))，空间复杂度O(1)\n
 * 默认对全体数组元素进行排序，如果需要对部分元素排序，请使用原函数\n
 * 除了int和double类型，其他类型应使用GenericShellSort宏定义对应的希尔排序函数
 * @example ShellSort(int, int_arr, FROM_SMALL_TO_BIG);
 * @sa GenericShellSort
 */

#define ShellSort(arr_type, arr, flag) shellSort_##arr_type(arr, sizeof(arr) / sizeof((arr)[0]), flag)

/*归并排序*/

#ifdef MergeSort
#undef MergeSort
#endif  //MergeSort

/**
 * @name MergeSort
 * @category 宏
 * @param arr_type 需要排序的数组的类型
 * @param arr 需要排序的数组
 * @param flag 对数组排序的方式
 * @details 归并排序，时间复杂度O(n log(n))，空间复杂度O(n)\n
 * 默认对全体数组元素进行排序，如果需要对部分元素排序，请使用原函数\n
 * 除了int和double类型，其他类型应使用GenericSelectionSort宏定义对应的归并排序函数
 * @example MergeSort(int, int_arr, FROM_SMALL_TO_BIG);
 * @sa GenericMergeSort
 */

#define MergeSort(arr_type, arr, flag) mergeSort_##arr_type(arr, sizeof(arr) / sizeof((arr)[0]), flag)

#ifdef IsUp
#undef IsUp
#endif  //IsUp

/**
 * @name IsUp
 * @category 宏
 * @param arr_type 需要判断的数组的类型
 * @param arr 需要判断的数组
 * @details 判断数组是否为升序排列
 * @example IsUp(int, int_arr);
 */

#define IsUp(arr_type, arr) isUp_##arr_type(arr, sizeof(arr) / sizeof((arr)[0]))

#ifdef IsDown
#undef IsDown
#endif  //IsDown

/**
 * @name IsDown
 * @category 宏
 * @param arr_type 需要判断的数组的类型
 * @param arr 需要判断的数组
 * @details 判断数组是否为降序排列
 * @example IsDown(int, int_arr);
 */

#define IsDown(arr_type, arr) isDown_##arr_type(arr, sizeof(arr) / sizeof((arr)[0]))

/*在C++中使用时，以C的方式调用*/
#ifdef __cplusplus
}
#endif  //__cplusplus

#endif //MY_SORT_HEADER__NJU_SE_2022__

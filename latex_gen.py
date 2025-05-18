from itertools import product

# Путь к папке с графиками
graphics_dir_dest = "./appendix_pics/"

# Генерируем LaTeX-код
latex_code = """
\\section*{Приложение 1. Результаты экспериментов с реализованными алгоритмами}
\\addcontentsline{toc}{section}{Приложение 1. Результаты экспериментов с реализованными алгоритмами}
\\label{sec:Appendix} \\index{Appendix}

В данном приложении приведены тепловые карты для серий экспериментов по сравнению энергопотребления при выполнении расписания алгоритмов. Формат тепловой карты описан в разделе 4.4. В ячейке тепловой карты указано процентное соотношение значения энергопотребления при построении расписания указанным алгоритмом и значения энергопотребления при построении расписания без использования механизмов энергосбережения в рамках конкретного эксперимента.

\\subsection*{Тепловые карты сравнения алгоритмов}

"""

CPU_count = [2, 5, 10, 20]
CPU_min_speed = [10, 25, 50]
static_P_percent = [0, 1, 5, 10, 20]

for numbers in product(CPU_count, CPU_min_speed, static_P_percent):
    filename = f'Experiment_{numbers[0]}_{numbers[1]}_{numbers[2]}.png'
    label = f"fig:exp_{numbers[0]}_{numbers[1]}_{numbers[2]}"
    caption = f'Снижение энергопотребления алгоритмов относительно выполнения без механизмов энергосбережения:\n{numbers[0]} процессоров, частота {numbers[1]}-100, Стат.мощность {numbers[2]}\%'

    latex_code += f"""
\\begin{{figure}}[H]
    \\centering
    %\\includegraphics[width=\\textwidth]{{{graphics_dir_dest}{filename}}}
    \\includegraphics[height=8cm]{{{graphics_dir_dest}{filename}}}
    \\caption{{{caption}}}
    \\label{{{label}}}
\\end{{figure}}

"""

# Записываем результат в файл
with open("graphics_insertions.tex", "w", encoding="utf-8") as f:
    f.write(latex_code)
# Записываем результат в файл
with open("../VKR/Appendix.tex", "w", encoding="utf-8") as f:
    f.write(latex_code)

print("LaTeX-код для вставки графиков сохранён в файл graphics_insertions.tex")
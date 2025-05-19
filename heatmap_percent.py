import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from glob import glob

from itertools import product

CPU_count = [2, 5, 10, 20]
CPU_min_speed = [50, 25, 10]
static_P_percent = [i for i in range(5)]

for count, speed, static_p_percent in product(CPU_count, CPU_min_speed, static_P_percent):
    percent = 0 if static_p_percent == 0 else (1 if static_p_percent == 1 else (5 if static_p_percent == 2 else (10 if static_p_percent == 3 else 20)))
    files = glob(f"VKR_results/Experiment_{count}_{speed}_{static_p_percent}.csv")
    base_files = glob(f"VKR_results/BaseData_{count}_{static_p_percent}.csv")
    df_list = []
    base_df_list = []

    for file in files:
        temp_df = pd.read_csv(file, header=None)
        df_list.append(temp_df)
    df = pd.concat(df_list, ignore_index=True)

    for base_file in base_files:
        base_temp_df = pd.read_csv(base_file, header=None)
        base_df_list.append(base_temp_df)
    base_df = pd.concat(base_df_list, ignore_index=True)


    # Назначение имен столбцам
    df.columns = ['Task_count', 'Deadline', 'NoMigNoDPM', 'MigNoDPM', 'NoMigDPM', 'MigDPM']
    base_df.columns = ['Task_count', 'Deadline', 'Base']

    # Группировка по количеству задач и дедлайну, вычисление среднего значения энергии
    heatmap_data = df.groupby(['Task_count', 'Deadline']).mean().reset_index()
    base_heatmap_data = base_df.groupby(['Task_count', 'Deadline']).mean().reset_index()
    
    for i in ['NoMigNoDPM', 'MigNoDPM', 'NoMigDPM', 'MigDPM']:
        heatmap_data[i] /= base_df['Base']
    
    # Определение общих границ для цветовой шкалы
    vmin = heatmap_data[['NoMigNoDPM', 'MigNoDPM', 'NoMigDPM', 'MigDPM']].min().min()
    vmax = 1.0


    # Настройки шрифта
    font_settings = {
        'annot_kws': {'size': 13},  # Размер шрифта аннотаций
        'fontsize': 10,             # Размер шрифта подписей осей
        'title_fontsize': 12        # Размер шрифта заголовков
    }

    # Создание фигуры с 4 субплoтами
    fig, axes = plt.subplots(2, 2, figsize=(8, 6))
    fig.suptitle(f'Снижение энергопотребления алгоритмов относительно выполнения без механизмов энергосбережения:\n{count} процессоров, частота {speed}-100, Стат.мощность {percent}%', fontsize=16)

    # Алгоритмы и их названия для отображения
    algorithms = ['NoMigNoDPM', 'MigNoDPM', 'NoMigDPM', 'MigDPM']
    titles = ['Алгоритм LTF', 'Алгоритм LTF-M', 'Алгоритм LTF-MES', 'Комбинированный алгоритм']

    # Построение тепловых карт для каждого алгоритма
    for i, (algo, title) in enumerate(zip(algorithms, titles)):
        ax = axes[i//2, i%2]  # Определение позиции субплoта
        pivot_table = heatmap_data.pivot(index='Task_count', columns='Deadline', values=algo)
        sns.heatmap(
            pivot_table, 
            annot=True, 
            fmt=".1%", 
            cmap="YlOrRd", 
            linewidths=.5, 
            ax=ax,  
            vmin=vmin,
            vmax=vmax,
            cbar_kws={'label': 'Энергия'},
            annot_kws={'size': font_settings['annot_kws']['size']}  # Применяем настройки шрифта
        )
        ax.set_title(title, fontsize=font_settings['title_fontsize'])
        ax.set_xlabel('Множитель дир.срока', fontsize=font_settings['fontsize'])
        ax.set_ylabel('Количество задач', fontsize=font_settings['fontsize'])
        ax.invert_yaxis()
        
    plt.tight_layout()
    #plt.savefig(f"../VKR/appendix_pics/Experiment_{count}_{speed}_{percent}.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"VKR_Graphics/Experiment_{count}_{speed}_{percent}.png", dpi=300, bbox_inches='tight')
    plt.close()
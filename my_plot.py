# Hulthén, K., Chapman, B. B., Nilsson, P. A., Hansson, L. A., Skov, C., Brodersen, J., & Brönmark, C. (2022). 
# Timing and synchrony of migration in a freshwater fish: Consequences for survival. Journal of Animal Ecology.
#
# - replicate one of their results to check I understand
# - plot synchrony for each lake, year, arrival and departure


import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt

# borrowed from: https://rafatieppo.github.io/post/2018_12_01_juliandate/
def datestdtojd (stddate):
    fmt='%Y-%m-%d'
    sdtdate = datetime.datetime.strptime(stddate, fmt)
    sdtdate = sdtdate.timetuple()
    jdate = sdtdate.tm_yday
    return(jdate)

# ---------------------------------


# parameters
# ---

# input file name
fname = 'JAE_Timing_2022.csv'


# get data
# ---

df = pd.read_csv(fname)


# append angle that corresponds to the date to df
# ---

# this makes the 1 january = 0, 31 december = 364
julian_days = [datestdtojd('-'.join(reversed(date.split('/'))))-1 for date in df['Date']]

# find the maximum value for each year (account for leap years)
# so the values will either be 364 or 365
max_days = [datestdtojd(date.split('/')[2] + '-12-30') for date in df['Date']]

# the angle in radians is 2*pi*julian_day/max_day
angles = [2*np.pi*julian_day/max_day for julian_day, max_day in zip(julian_days, max_days)]

# append to df
df['angle'] = angles


# append the x and y components of the vector
# ---

xs = [np.sin(angle) for angle in df['angle']]
ys = [np.cos(angle) for angle in df['angle']]

df['x'] = xs
df['y'] = ys



# split data up for plotting
# ---

# get range
arrdeps = ['Arrival', 'Departure']
lakes = sorted(set(df['Lake']))

# for columns in results df
yearV = list()
arrdepV = list()
lakeV = list()

# rho is mean vector length
rhoV = list()
for arrdep in arrdeps:

    df_sub = df[df['Departure/Arrival'] == arrdep]

    for lake in lakes:

        df_subb = df_sub[df_sub['Lake'] == lake]

        # different year range different lakes
        years = sorted(set(df_subb['Year']))

        for year in years:

            # append to columns
            yearV.append(year)
            arrdepV.append(arrdep)
            lakeV.append(lake)

            # calculate rho and append
            df_subbb = df_subb[df_subb['Year'] == year]
            x_mean = np.mean(df_subbb['x'])
            y_mean = np.mean(df_subbb['y'])
            rho = np.sqrt(x_mean**2 + y_mean**2)
            rhoV.append(rho)

df_res = pd.DataFrame(data = {'year': yearV, 'arrdep': arrdepV, 'lake': lakeV, 'rho': rhoV})


# plot
# ---

plt.figure(figsize=(6, 3.8))

# mapping from year to xtick
all_years = sorted(set(df['Year']))
year2tic = {year: i for i, year in enumerate(all_years)}

# remap "Arrival" to "Spring" and "Departure" to Autumn
remapD = {"Arrival": "Spring", "Departure": "Autumn"}

for colour, arrdep in zip(['red', 'blue'], arrdeps):
    for shape, lake in zip(['o', '*'], lakes):

        df_sub = df_res[df_res['arrdep'] == arrdep]
        df_sub = df_sub[df_sub['lake'] == lake]

        # different year range different lakes
        years = sorted(set(df_sub['year']))
        tics = [year2tic[year] for year in years]

        rhoV = df_sub['rho']

        # means
        print(f'{arrdep}, {lake}')
        print(np.mean(rhoV))

        plt.plot(tics, rhoV, '-'+shape, alpha=0.5, color=colour, label = remapD[arrdep] + ' ' + lake)

# shorten the year string
all_years = [year[:4] + '/\n' + year[5:9] for year in all_years]
plt.legend(loc='best', ncol=2)
plt.xlabel('year', fontsize='x-large')
plt.ylim((-0.1,1.1))
plt.xticks(ticks=range(len(all_years)), labels=all_years)
plt.ylabel(r'synchrony, $\rho$', fontsize='x-large')
plt.tight_layout()
plt.savefig('my_plot.pdf')
plt.close()

# my mean values are close to theirs
#
# they wrote: We also found that spring arrival timing to the lake habitat was more synchronized among individuals, as quantified by mean vector lengths (r), as compared to the autumn lake departure, a pattern also shared across lakes (Krankesjön spring arrival: mean r = 0.924, autumn departure: mean r = 0.743; t-test, p= 0.0002; Søgård Sø spring arrival: mean r = 0.981, autumn departure: mean r = 0.690, Mann-Whitney U-test, p=0.003)
#
# my results were:
#
# Arrival, Krankesjön
# 0.925142        they got 0.924 <- typo?
# Arrival, Sogård
# 0.981200        they got 0.981
# Departure, Krankesjön
# 0.743902        they got 0.743 <- rounding?
# Departure, Sogård
# 0.690698        they got 0.690

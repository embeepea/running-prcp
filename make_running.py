#! /usr/bin/python

import sys, re
sys.path.append('py-normals')
from StationNormals import StationNormals
from Dly import Dly

def ytd_to_daily_prcp(ytd_prcp):
    """Converts ytd precip to daily prcp.  ytd_prcp should be a 2D array of the form
    ytd_prcp[m][d], where m is the (0-based) month number and d is the (0-based) day
    number.  Returns a 2D array of the same form where the entries represent daily
    prcp amounts."""
    data = []
    prev = None
    for ytd_vals in ytd_prcp:
        daily_vals = []
        for val in ytd_vals:
            if val >= 0:
                if prev == None:
                    daily_val = val
                else:
                    daily_val = val - prev
                daily_vals.append(daily_val)
                prev = val
        data.append(daily_vals)
    return data

def daily_normal_prcp_to_running_prcp(daily_normal_prcp, N):
    """Converts a daily normal prcp array to a running total normal prcp array.  daily_normal_prcp should be
    a 2D array of the form daily_normal_prcp[m][d], where m is the (0-based) month number and d
    is the (0-based) day number.  Returns a 2D array of the same form where the entries represent running
    totals for the last N days."""
    data = [];
    # pre-populate data array with `None`s
    data = [ [None for d in m] for m in daily_normal_prcp ]
    # we use the `running` array to store the last N values while computing the running sums
    running = []
    # go through data once, populating results, skipping the first N-1 entries (leaving them None)
    for m in range(0,len(daily_normal_prcp)):
        for d in range(0,len(data[m])):
            p = daily_normal_prcp[m][d]
            if len(running) >= N:
                running.pop()
                running.insert(0,p)
            else:
                running.insert(0,p)
            if len(running) == N:
                data[m][d] = sum(running)
    # go through data one more time, to populate Nones at beginning:
    done = False
    for m in range(0,len(daily_normal_prcp)):
        if done:
            break
        for d in range(0,len(data[m])):
            if data[m][d] != None:
                done = True
                break
            p = daily_normal_prcp[m][d]
            running.pop()
            running.insert(0,p)
            data[m][d] = sum(running)
    return data

def daily_prcp_to_running_prcp(daily_prcp, daily_normal_prcp, N):
    """Converts a daily prcp array to a running total prcp array.  daily_prcp should be
    a array whose elements are objects of the form
       { 'year' : 1948, 'month' : 7, values : [ ... ] }
    (note that the month numbers in daily_prcp are 1-based!)  daily_normal_prcp should be
    an array of the form daily_normal_prcp[m][d], where m is the (0-based) month number
    and d is the (0-based) day number.  Returns an array of the same form as daily_prcp,
    in which the entries represent running totals for the last N days.  For any days
    in daily_prcp that have missing data, the corresponding day's value from daily_normal_prcp
    is used."""
    data = [];
    running = []
    for m in daily_prcp:
        year  = m['year']
        month = m['month']
        values = []
        for i in range(0,len(m['values'])):
            v = m['values'][i]
            if v < 0:
                if i < len(daily_normal_prcp[month-1]):
                    v = daily_normal_prcp[month-1][i]
                else:
                    v = None
            if v is not None:
                if len(running) >= N:
                    running.pop()
                running.insert(0, v if v is not None else daily_normal_prcp[year][month-1])
                values.append(sum(running) if len(running)==N else None)
        data.append({ 'year' : year, 'month' : month, 'values' : values })
    return data

def print_normal_data(data):
    for m in data:
        print " ".join([ ('***' if v is None else ("%4d" % v)) for v in m ])

def print_data(data):
    for y in data:
        print "%04d-%02d  %s" % (y['year'], y['month'], " ".join([ ('  **' if v is None else ("%4d" % v)) for v in y['values'] ]))

def write_daily_dat_file(daily_prcp, filename):
    f = open(filename, 'w')
    for m in daily_prcp:
        if m['values'][0] is None:
            continue
        f.write("%04d%02d,%s\n" % (m['year'], m['month'], ",".join( (str(x) if x is not None else 'M')  for x in m['values'])))
    f.close()

def write_normal_dat_file(daily_normal_prcp, filename):
    f = open(filename, 'w')
    for m in range(0,12):
        f.write("2010%02d,%s\n" % (m+1, ",".join([str(x) for x in daily_normal_prcp[m]])))
    f.close()

def write_running_data_and_normals(dly_input_filename,                 # USC00010008.dly
                                   normals_input_filename,              # USC00010008.normals.txt
                                   running_data_output_filename,
                                   running_normals_output_filename,
                                   N):
    s = StationNormals(normals_input_filename)
    d = Dly(dly_input_filename)
    ytd_normal_prcp     = s.normals['Precipitation-Related']['Daily']['ytd-prcp-normal']
    daily_normal_prcp   = ytd_to_daily_prcp(ytd_normal_prcp)
    running_normal_prcp = daily_normal_prcp_to_running_prcp(daily_normal_prcp, N)
    daily_prcp          = d.data['PRCP']
    running_prcp        = daily_prcp_to_running_prcp(daily_prcp, daily_normal_prcp, N)
    write_daily_dat_file(running_prcp, running_data_output_filename)
    print "wrote %s" % running_data_output_filename
    write_normal_dat_file(running_normal_prcp, running_normals_output_filename)
    print "wrote %s" % running_normals_output_filename

### write_running_data_and_normals('USC00010008.dly',
###                                'USC00010008.normals.txt',
###                                'foo-data.dat',
###                                'foo-normals.dat',
###                                30)

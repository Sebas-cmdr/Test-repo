# Created by sebas on 25.11.2023 at 18:01
# =============================================================================
# 2.8 Missing Values
# =============================================================================
'''
We’ve seen a preview of how Pandas handles missing values using the None type and NumPy NaN
values. Missing values are pretty common in data cleaning activities. And, missing values can be
there for any number of reasons, and I just want to touch on a few here.
For instance, if you are running a survey and a respondant didn’t answer a question the missing
value is actually an omission. This kind of missing data is called Missing at Random if there
are other variables that might be used to predict the variable which is missing. In my work when
I deliver surveys I often find that missing data, say the interest in being involved in a follow
up study, often has some correlation with another data field, like gender or ethnicity. If there
is no relationship to other variables, then we call this data Missing Completely at Random
(MCAR).
These are just two examples of missing data, and there are many more. For instance, data might
be missing because it wasn’t collected, either by the process responsible for collecting that data,
such as a researcher, or because it wouldn’t make sense if it were collected. This last example
is extremely common when you start joining DataFrames together from multiple sources, such as
joining a list of people at a university with a list of offices in the university (students generally
don’t have offices).
Let’s look at some ways of handling missing data in pandas.
'''

# Lets import pandas
import pandas as pd

# Pandas is pretty good at detecting missing values directly from underlying data formats, like CSV files. Although most
# missing values are often formatted as NaN, NULL, None, or N/A, sometimes missnig values are not labeled so clearly.
# For example, I've worked with social scientists who regularly used the value of 99 in binary categories to indicate a
# missing value. The pandas read_csv() function has a parameter called na_values to let us specify the form of missing
# values. It allows scalar, string, list, or dictionaries to be used

# Let's load a piece of data from a file called class_grades.csv
df = pd.read_csv('datasets/class_grades.csv')
df.head(10)

# We can actually use the function .isnull() to create a boolean mask of the whole DF. This effectively broadcasts the
# isnull() function to every cell of data
mask=df.isnull()
mask.head(10)
# ((the isnull gives True for all NaN in DF))
# This can be useful for processing rows based on certain columns of data. Another useful operation is to be able to
# drop all of those rows which have any missing data, which can be done with the dropna() function.
df.dropna().head(10)

# Note how the rows indexed with 2,3,7 and 11 are now gone. One of the handy functions that Pandas has for working with
# missing values is the filling function, fillna(). This function takes a number or parameters. You could pass in a
# single value which is called a scalar value to change all of the missing data to one value. This isn't really
# applicable in this case, but it's a pretty common use case. E.g. fill all missing values with 0
df.fillna(0, inplace=True)
df.head(10)

# Note that the inplace attribute causes pandas to fill the values inline and does not return a copy of the DF, but
# instead modifies the DF you gave
# ((therefore, with inplace=True we can't chain .head directly, but with inplace =False, we can do it))
df.fillna(0, inplace=False).head(10)

# We can also use the na_filter option to turn off white space filtering, if white space is an actual value of interest.
# But in practice, this is pretty rare. In data without any NAs, passing na_filter=False, can improve the performance
# of reading a large file.
# In addition to rules controlling how missing values might be loaded, it's sometimes useful to consider missing values
# as actually having information. Example: I often deal with logs from online learning systems. I've looked at video use
# in lecture capture systems. In these systems it's common for the player to have a heartbeat functionality where
# playback statistics are sent to the server every so often, maybe every 30 seconds. These heartbeats can get big as
# they can carry the whole state of the playback system such as where the video play head is at, where the video size
# is, which video is being rendered to the screen, how loud the volume is.
# If we load the data file log.csv, we can see an example of what this might look like.
df = pd.read_csv('datasets/log.csv')
df.head(20)

# In this data the first column is a timestamp in the Unix epoch format. The next column is the user name followed by a
# web page they're visiting and the video that they're playing. Each row of the DF has a playback position. And we can
# see that as the playback position increases by one, the timestamp increases by about 30 seconds.
# Except for user Bob. It turns out that Bob has paused his playback so as time increases the playback position doesn't
# change. Note too how difficult it is for us to try and derive this knowledge from the data, because it's not sorted
# by time stamps as one might expect. This is actually not uncommon on systems which have a high degree of parallelism.
# There are a lot of missing values in the paused and volume columns. It's not efficient to send this information across
# the network if it hasn't changed. So this particular system just inserts null values into the database if there's no
# changes.

# Next up is the method of parameter(). The 2 common fill values are ffill and bfill. ffill is for forward filling and
# it updates an na value for a particular cell with the value from the previous row. bfill is backward filling, which
# is the opposite of ffill. It fills the missing values with the next valid value. It's important to note that your data
# needs to be sorted in order for this to have the effect you might want. Data which comes from traditional database
# management systems usually has no order guarantee, just like this data. So be careful.

# In Pandas we can sort either by index or by values. Here we'll just promote the time stamp to an index then sort on it
df = df.set_index('time')
df = df.sort_index()
df.head(20)

# If we look closely at the output though we'll notice that the index isn't really unique. 2 users seem to be able to
# use the system at the same time. Again, a very common case. Let's reset the index, and use some multi-level indexing
# on time AND user together instead. Promote the user name to a second level of the index to deal with that issue:
df=df.reset_index()
df=df.set_index(['time','user'])
df.head(20)

# Now that we have the data indexed and sorted appropriately, we can fill the missing datas using ffill. It's good to
# remember when dealing with missing values so you can deal with individual columns or sets of columns by projecting
# them. So you don't have to fix all missing values in one command.
df = df.fillna(method='ffill')
df.head()

# We can also do customized fill-in to replace values with the replace() function. It allows replacement from several
# approaches: value-to-value, list, dictionary, regex. Let's generate a simple example
df = pd.DataFrame({'A':[1,1,2,3,4],
                   'B':[3,6,3,8,9],
                   'C': ['a', 'b', 'c', 'd', 'e']})
df

# We can replace 1's with 100, let's try the value-to-value approach
df.replace(1,100)
# How about changing two values? Let's try the list approach. For example, we want to change 1's to 100 and 3's to 300
df.replace([1,3],[100,300])

# What's really cool about pandas replacement is that it supports regex too! Let's look at our data from the log.csv
df = pd.read_csv('datasets/log.csv')
df.head(20)

# To replace using a regex we make the first parameter to replace the regex pattern we want to match, the second
# parameter the value we want to emit upon match, and then we pass in a third parameter "regex=True".
# Take a moment to pause and think about this problem: imagine we want to detect all html pages in the "video" column,
# let's say that just means they end with ".html", and we want to overwrite that with the keyword "webpage". How could
# we accomplish this?
# Here's my solution, first matching any number of characters, then ending in .html
df.replace(to_replace=".*.html$", value="webpage", regex=True)
# remember: dollar sign character $ means end (it's an anchor markup)

'''
One last note on missing values. When you use statistical functions on DataFrames, these functions
typically ignore missing values. For instance if you try and calculate the mean value of a DataFrame,
the underlying NumPy function will ignore missing values. This is usually what you want but you
should be aware that values are being excluded. Why you have missing values really matters
depending upon the problem you are trying to solve. It might be unreasonable to infer missing
values, for instance, if the data shouldn’t exist in the first place.
'''

# =============================================================================
# 2.8 DF Manipulation
# =============================================================================
'''
Now that you know the basics of what makes up a pandas dataframe, lets look at how we might
actually clean some messy data. Now, there are many different approaches you can take to clean
data, so this lecture is just one example of how you might tackle a problem
'''
import pandas as pd
dfs=pd.read_html("https://en.wikipedia.org/wiki/College_admissions_in_the_United_States")
len(dfs)
dfs[10]

'''
Python programmers will often suggest that there are many ways the language can be used to solve
a particular problem. But that some are more appropriate than others. The best solutions are
celebrated as Idiomatic Python and there are lots of great examples of this on StackOverflow and
other websites.
A sort of sub-language within Python, Pandas has its own set of idioms. We’ve alluded to some
of these already, such as using vectorization whenever possible, and not using iterative loops if you
don’t need to. Several developers and users within the Panda’s community have used the term
pandorable for these idioms. I think it’s a great term. So, I wanted to share with you a couple of
key features of how you can make your code pandorable.
'''
import numpy as np
import timeit

df = pd.read_csv('datasets/census.csv')
df.head()

# The first of these is called method chaining. The general idea behind method chaining is that every method on an
# object returns a reference to that object. The beauty of this is that you can condense many different operations on a
# DF, for instance, into on line or at least one statement of code. Here's an example of 2 pieces of code in pandas
# using our census data
# The first is the pandorable way to write the code with method chaining. In this code, there's no in place flag being
# used and you can see that when we first run a where query, then dropna, then a set_index, and then a rename.
# ((Remember: inplace=True attribute causes pandas to fill the values inline and does not return a copy of the DF, but
# instead modifies the DF you gave))
# You might wonder why the whole statement is enclosed in parentheses and that's just to make the statement more
# readable
(df.where(df['SUMLEV']==50)
    .dropna()
    .set_index(['STNAME','CTYNAME'])
    .rename(columns={'ESTIMATESBASE2010':'Estimates Base 2010'}))

# The second example is a more traditional way of writing code. There's nothing wrong with this code in the functional
# sense, you might even be able to understand it better as a new person to the language. It's just not as pandorable as
# the first example.
df = df[df['SUMLEV']==50]
df.set_index(['STNAME','CTYNAME']).rename(columns={'ESTIMATESBASE2010':'Estimates Base 2010'})
# ((Important diff: in 1 we don't change the original data, in 2 we actually only keep SUMLEV==50))


# Now, the key with any good idiom is to understand when it isn't helping you. In this case, you can actually time both
# methods and see which one runs faster.
# We can put the approach into a function and pass the function into the timeit function to count the time.
# The parameter number allows us to choose how many times we want to run the function. Here we will just set it to 1
df = pd.read_csv('datasets/census.csv')
def first_approach():
    global df
    return (df.where(df['SUMLEV']==50)
                .dropna()
                .set_index(['STNAME','CTYNAME'])
                .rename(columns={'ESTIMATESBASE2010':'Estimates Base 2010'}))

timeit.timeit(first_approach, number=1)
df
# ((We didn't introduce the global command; it seems to call any variable/data that has been loaded already and that
# is not necessarly defined within the new function being written, but outside of it))

# Now let's test the second approach. As we note, we use our global variable df in the function. However, changing a
# global variable inside a function will modify the variable even in a global scope and we do not want that to happen
# in this case. Therefore, for selecting summary levels of 50 only, I create a new DF for those records. Let's run
# this for once and see how fast it is
def second_approach():
    global df
    new_df = df[df['SUMLEV']==50]
    new_df.set_index(['STNAME', 'CTYNAME'], inplace=True)
    return new_df.rename(columns={'ESTIMATESBASE2010':'Estimates Base 2010'})
timeit.timeit(second_approach, number=1)

# As you can see, the second approach is much faster! So, this is a particular example of a classic time readability
# trade-off.
# You'll see lots of examples on stack overflow and in documentation of people using method chaining in their pandas.
# And so, I think being able to read and understand the syntax is really worth your time.

# Here's another pandas idiom. Python has a wonderful function called map, which is sort of a basis for functional
# programming in the language. When you want to use map in Python, you pass it some function you want called, and some
# iterable, like a list, that you want the function to be applied to. The results are that the function is called
# against each item in the list, and there's a resulting list of all of the evaluations of that function.

# Python has a similar function called applymap. In applymap, you provide some function which should operate on each
# cellof a DF, and the return set is itself a DF. Now I think applymap is fine, but I actually rarely use it. Instead,
# I find myself often wanting to map across all of the rows in a DF. And Pandas has a function that I use heavily here,
# called apply. Let's look at an example.

# Let's take our census DF. In this DF, we have five columns for population estimates. Each column corresponding with
# one year of estimates. It's quite reasonable to want to create some new columns for minimum or max values, and the
# apply function is an easy way to do this.
# First, we need to write a function which takes in a particular row of data, finds a minimum and maximum values, and
# returns a new row of data. We'll call this function min_max, this is pretty straight forward. We can create some small
# slice of a row by projecting the population columns. Then use the NumPy min and max functions, and create a new series
# with a label where values represent the new values we want to apply
def min_max(row):
    data = row[['POPESTIMATE2010',
                'POPESTIMATE2011',
                'POPESTIMATE2012',
                'POPESTIMATE2013',
                'POPESTIMATE2014',
                'POPESTIMATE2015']]
    return pd.Series({'min': np.min(data), 'max': np.max(data)})

# Then we just need to call apply on the DF
# Apply takes the function and the axis on which to operate as parameters. Now, we have to be a bit careful, we've
# talked about axis zero being the rows of the DF in the past. But this parameter is really the parameter of the index
# to use. So, to apply accross all rows, which is applying on all columns, you pass axis equal to one.
df.apply(min_max, axis=1)

# Of course, there's no need to limit yourself to returning a new series object. If you're doing this as part of data
# cleaning you're likely to find yourself wanting to add new data to the existing DF. In that case you just take the
# row values and add in new columns indicating the max and min scores. This is a regular part of my workflow when
# bringing in data and building summary or descriptive statistics. And is often used heavily with the merging of DFs.

# Here we have a revised version of the function min_max. Instead of returning a separate series to display the min and
# max, we add two new columns in the original DF to store min and max
def min_max(row):
    data = row[['POPESTIMATE2010',
                'POPESTIMATE2011',
                'POPESTIMATE2012',
                'POPESTIMATE2013',
                'POPESTIMATE2014',
                'POPESTIMATE2015']]
    row['max'] = np.max(data)
    row['min'] = np.min(data)
    return row
df.apply(min_max, axis=1)

# ((Note: we apply the function to df, therefore the parameter row will actually represent df and we will get the rows
# of df that we want per the usualy indexing ([]) conventions; see below which subset of data we are using))
df[['POPESTIMATE2010',
                'POPESTIMATE2011',
                'POPESTIMATE2012',
                'POPESTIMATE2013',
                'POPESTIMATE2014',
                'POPESTIMATE2015']]

# Apply is an extremely important tool in your toolkit. The reason I introduced apply here is because you rarely see it
# used with large function definitions, like we did. Instead, you typically see it used with lambdas. To get the most
# of the discussions you'll see online, you're going to need to know how to at least ready lambdas.

# You can imagine how you might chain several apply calls with lambdas together to create a readable yet succinct data
# manipulation script. One line example of how you might calculate the max of the columns using the apply function
rows = ['POPESTIMATE2010',
        'POPESTIMATE2011',
        'POPESTIMATE2012',
        'POPESTIMATE2013',
        'POPESTIMATE2014',
        'POPESTIMATE2015']
# ((Note that rows is just a list of strings))
df.apply(lambda x: np.max(x[rows]), axis=1)  # ((x[rows] is like df['POPESTIMATE2010', ...]

# The beauty of the apply function is that it allows flexibility in doing whatever manipulation that you desire, and
# the function you pass into apply can be any customized function that you write. Let's say we want to divide the states
# into four categories: Northeast, Midwest, South and West. We can write a customized function that returns the region
# based on the state. The state regions information is obtained from Wikipedia
def get_state_region(x):
    northeast = ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire','Rhode Island','Vermont','New York',
                 'New Jersey', 'Pennsylvania']
    midwest = ['Illinois', 'Indiana', 'Michigan', 'Ohio', 'Wisconsin', 'Iowa',
               'Kansas', 'Minnesota', 'Missouri', 'Nebraska', 'North Dakota',
               'South Dakota']
    south = ['Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina',
             'South Carolina', 'Virginia', 'District of Columbia', 'West Virginia',
             'Alabama', 'Kentucky', 'Mississippi', 'Tennessee', 'Arkansas',
             'Louisiana', 'Oklahoma', 'Texas']
    west = ['Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah',
            'Wyoming', 'Alaska', 'California', 'Hawaii', 'Oregon', 'Washington']

    if x in northeast:
        return "Northeast"
    elif x in midwest:
        return "Midwest"
    elif x in south:
        return "South"
    else:
        return "West"

# Now we have the customized function, let's say we want to create a new column called Region, which shows the state's
# region, we can use the customized function and the apply function to do so. The customized function is supposed to
# work on the state name column STNAME. So we will set the apply function on the state name column and pass the
# customized function into the apply function
df['state_region'] = df['STNAME'].apply(lambda x: get_state_region(x))
# Now let's see the results
df[['STNAME','state_region']]

'''
So there are a couple of Pandas idioms. But I think there’s many more, and I haven’t talked about
them here. So here’s an unofficial assignment for you. Go look at some of the top ranked questions
on pandas on Stack Overflow, and look at how some of the more experienced authors, answer those
questions. Do you see any interesting patterns? Chime in on the course discussion forums and let’s
build some pandorable documents together.
'''
---
layout: main
---

Why win_unc?
============

This library is for anyone who has tried to connect to or mount UNC paths in a Python
script on Windows. Understanding how to wield the `NET USE` command is a feat
in itself. Parsing its output programatically to know if your command worked is much
harder.

Fortunately, this library should make your life a lot easier.


Contents
========

* This list will contain the toc (it doesn't matter what you write here)
{:toc}


Installation
============

To install:

    $ pip install win_unc


Getting pip on Windows
----------------------

Of course, installing `pip` packages on Windows is not always straightforward.
Here's how:

Download the [setuptools installer](http://pypi.python.org/pypi/setuptools) for your platform and
run it. **Note that for 64-bit Windows, you need to download the `ez_setup.py` script instead of
the `.exe` installer.

Once you've installed `setuptools`, you need to add some paths to your system's `Path`
environment variable. You'll probably want to add paths like these:

*	`C:\Python27`
*	`C:\Python27\Scripts`

Then, in Windows command-line (`cmd.exe`), you can run the following to get `pip`
installed:

    > easy_install pip


Basic Usage
===========

Below is a simple example:

{% highlight python %}
from win_unc import UncDirectoryMount, UncDirectory, DiskDrive

conn = UncDirectoryMount(UncDirectory(r'\\home\shared'), DiskDrive('Z:'))
conn.connect()
print 'Drive connected:', conn.is_connected()
conn.disconnect()
{% endhighlight %}

You can also provide credentials like this

{% highlight python %}
from win_unc import UncCredentials

unc = UncDirectory(r'\\home\shared', UncCredentials('user', 'pwd'))
conn = UncDirectoryMount(unc, DiskDrive('Z:'))
{% endhighlight %}


Documentation
=============

UncDirectoryConnection {#UncDirectoryConnection}
----------------------

The `UncDirectoryConnection` class describes how a UNC directory relates to the current
Windows sesssion. Use this class when you want to connect or disconnect a UNC directory. You can
also use it to determine if a UNC directory is connected or not.


### \_\_init\_\_

{% highlight python %}
UncDirectoryConnection(
    unc_directory,
    disk_drive=None,
    persistent=False,
    logger=no_logging)
{% endhighlight %}

Constructs a new `UncDirectoryConnection` object.

*	`unc_directory` must be a [UncDirectory][] object which provides a UNC path and
	any credentials necessary to authorize the connection.

*	`disk_drive` must be `None` or a [DiskDrive][] object.
	*	If `None`, connecting this UNC directory will not create a local mount point.
	*	If a `DiskDrive`, connecting this UNC directory will create a local mount point at the
		drive letter specified by `disk_drive`.

*	`persistent` must be `True` if you want the UNC directory connection to persist across
	multiple Windows sessions. Otherwise, set this to `False` (the default).

*	`logger` must be a function that takes a single string argument. The function will be called
	whenever the object does something worthy of being logged.


### connect

{% highlight python %}
connect()
{% endhighlight %}

Connects the UNC directory. This will make at most three connection attempts with different
credential configurations in case the credentials provided are not necessary (which is likely
when the credentials are saved by Windows from a previous connection). If the command fails, a
`ShellCommandError` will be raised.

### disconnect

{% highlight python %}
disconnect()
{% endhighlight %}

Disconnects the UNC path. If the command fails, this will raise a `ShellCommandError`.


### is_connected

{% highlight python %}
is_connected()
{% endhighlight %}

Returns `True` if the system registers this `UncDirectoryConnection` as connected. A UNC path is
considered connected if the system reports its status as either `OK` or `Disconnected`.

In the context of the system, a status of `Disconnected` means that the UNC path's connection has
been authorized and connected, but it is temporarily disconnected.

To refresh the connection of a `Disconnected` UNC path, you can usually just perform some trivial
task with the directory. For example, you could query its contents like this:

    > dir \\unc\path

This commonly refreshes the UNC connection and restores its status to `OK`.


UncDirectory {#UncDirectory}
------------

The `UncDirectory` class describes the path to a UNC directory and (optionally) any credentials
that are needed to authorize the connection to the path.

### \_\_init\_\_

{% highlight python %}
UncDirectory(
    path,
    unc_credentials)
{% endhighlight %}

-----

{% highlight python %}
UncDirectory(
    unc_directory)
{% endhighlight %}

Constructs a new `UncDirectory` object as a clone of `unc_directory`. The clone will be a "shallow"
copy, so the underlying [UncCredentials][] object used by the clone will have the same `id` as the
original.

*	`unc_directory` must be a [UncDirectory][] object to clone.


UncCredentials {#UncCredentials}
--------------


DiskDrive {#DiskDrive}
---------


[DiskDrive]: #DiskDrive
[UncCredentials]: #UncCredentials
[UncDirectory]: #UncDirectory
[UncDirectoryConnection]: #UncDirectoryConnection


License
=======
This package is released under the [MIT License](http://www.opensource.org/licenses/mit-license.php).


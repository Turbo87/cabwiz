# cabwiz

by Tobias Bieniek

cabwiz is a drop-in replacement for the proprietary cabwiz.exe application of Microsoft. 
It reads basic INF files like cabwiz.exe does and transforms the data into metadata
for the Pocket PC installer.

## Dependencies

The cabwiz script relies on

* lcab (https://launchpad.net/ubuntu/+source/lcab/) and
* python (http://www.python.org/)

cabwiz was developed and tested with python 2.7.

## Usage

<pre>
  cabwiz &lt;inf-file&gt; [/dest &lt;dest-dir&gt;] [/err &lt;err-file&gt;] [/cpu &lt;cpu-type&gt;] [/platform &lt;platform-name&gt;] [/v]
   
  inf-file       INF source file to use
  dest-dir       absolute dest dir for CAB files
  err-file       error file
  cpu-type       cpu types to support in the INF file
  platform-name  the name of the platform to support in the INF file
  v              verbose output
</pre>

err-file, cpu-type and platform-name aren't supported yet. cpu-type however is appended to the output filename.

## License

See LICENCE file.

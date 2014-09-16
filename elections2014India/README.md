Election summary
---------

Collects info from [eci](http://eciresults.nic.in) and populates the summary in a simple
html file (Im not good at styling things!)

The following details are shown for the winner and runner-up
* Name of candidate
* Party
* votes in favor 

Run [this jar](https://github.com/dotslash/elections/blob/master/ElecitonsNic/out/artifacts/ElectionsNic_jar/ElectionsNic.jar) or [this jar](https://github.com/dotslash/elections/blob/master/ElecitonsNic/out/artifacts/ElectionsNic_jar2/ElectionsNic.jar) and the elections results will be generated in the form of html in (user-home)/electionResults.html

    java -jar /path/to/ElectionsNic.jar

The difference between the first and the second jar file is that the the second one is multi-threaded version of the first and takes 2-4 seconds while the first one takes ~8-10 secs to complete.

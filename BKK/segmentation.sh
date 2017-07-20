#!/bin/sh
# usage: preprocessing/export IMSI

##################################################################################################
mcfly=`date --date="+110 minutes" +%s%N | cut -b1-13` #because the timestamp is +02, and the server is +00 (timezone)
##################################################################################################

##################################################################################################
path=`mktemp -d --tmpdir=/home/cserjesi/titkos-project/devel/python/tmp`
chmod a+wrx $path
##################################################################################################

#test data1
#end=1500050700000
#end=1500306300000
#end=1500480655736 #CAR false was 169E BUS
end=1500496500000 #BUS tail was true 975E
start=$((end-15*60*1000))
startdate=`date -d @$((start/1000)) +'%Y-%m-%d %H:%M:%S%:::z'`
enddate=`date -d @$((end/1000)) +'%Y-%m-%d %H:%M:%S%:::z'`

echo $start
# Export and preprocess terminal data
f=`echo "create table tmp_export as select \"locationTs\", \"userId\", lat, lon, accuracy, mcc, mnc, cid, \"cellTs\", mode, confidence, to_timestamp(\"locationTs\" / 1000)::date from locationdata_locationreport where \"locationTs\" > $start and \"locationTs\" < $end and \"userId\" = $1 order by \"locationTs\", \"cellTs\";" > query.sql`
f=`echo "copy tmp_export to '$path/terminal.txt' delimiter E'\\t' NULL AS '';" >> query.sql`
f=`echo "drop table tmp_export;" >> query.sql`
psql -U postgres publictransport < query.sql
f=`cat $path/terminal.txt | preprocessing/preprocess_terminal_backend_data.py > $path/terminal.json`

##################################################################################################
var=`date --date="110 minute ago" +'%Y-%m-%d %H:%M:%S%:::z'`
##################################################################################################

#test data1
#startdate="2017-07-14 16:20:00+00"
#enddate="2017-07-14 16:45:00+00"
#startdate="2017-07-17 15:30:00+00"
#enddate="2017-07-17 15:45:00+00"
#startdate="2017-07-19 16:01:00+00"
#enddate="2017-07-19 16:11:00+00"


# Export and preprocess futar data
# TODO: filter on last 10 minutes (unix timestamp vs. date)
echo "create table tmp as select * from vehicledatashort where lastupdatetime > '$startdate' and lastupdatetime < '$enddate';" > query.sql
cat futar_db/export_view.sql | sed 's/vehicledatashort/tmp/g' >> query.sql
echo "copy (select * from vehicledata_export) to '$path/futar.txt' delimiter E'\\t' NULL AS '';" >> query.sql
echo "drop view vehicledata_export;" >> query.sql
echo "drop table tmp;" >> query.sql
psql -U postgres publictransport < query.sql
bzip2 -f $path/futar.txt

# remove temporary query file
rm query.sql


# TODO: use $path files instead of ...


#echo "Pre-processing BKK FUTAR logs..."
bzcat $path/futar.txt.bz2 | preprocessing/preprocess_futar_data.py > $path/futar.txt

# Copy last terminal location record with 1 hour later ts 60*60*1000 milisec = 3600000


a=`tail -n 1 $path/terminal.json | cut -f 1`
b=$(($a+3600000))
tail -n 1 $path/terminal.json | sed "s/$a/$b/g" >> $path/terminal.json

#echo $path


#echo "Pre-processing terminal logs for GPS location based analysis..."
sort $path/terminal.json | preprocessing/location_outlier_filter.py GPS | sort > $path/terminal_gps.txt
#echo $path

#echo "Merge-sorting FUTAR and terminal logs for GPS location based analysis..."
sort -m $path/terminal_gps.txt $path/futar.txt | gzip -c > $path/merged_gps.txt.gz



# TODO: use $path files instead of ../../raw_data/2017.*

# calculation based on GPS terminal location
#echo "Trip segmentation and transport modality assignment based on terminal GPS locations..."
zcat $path/merged_gps.txt.gz | correlation/segment.py GPS > $path/correlated_segments_gps.json
jq -c '[.location_history[0].ts, .]' $path/correlated_segments_gps.json | sort |  jq -c '.[1]' | graph_search/graph_gps.py > $path/paths_gps.json
cat $path/paths_gps.json | graph_search/graph_json2txt.py > $path/paths_gps.txt

echo $path
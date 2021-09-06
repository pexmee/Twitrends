###############################################################################
#spec file for twitter_trends
################################################################################
Summary: A program that listens to new tweets containing a keyword and pattern
Name: twitrends
Version: 1.0.0
Release: 1
License: MIT
URL: https://github.com/pexmee
Group: System
Packager: Peter Yliniemi
BuildRoot: ~/rpmbuild/

# Build with the following syntax:
# rpmbuild --target noarch -bb twitter_trends.spec

%description
Twitter trends enables a user with access to the twitter API to listen to tweets 
with a specific keyword and pattern, sending the data instantaneously to 
an Elasticsearch instance. 

%prep
################################################################################
# Create the build tree and copy the files from the development directories    #
# into the build tree.                                                         #
################################################################################
echo "BUILDROOT = $RPM_BUILD_ROOT"
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/
mkdir -p $RPM_BUILD_ROOT/usr/local/log/
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system/
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/Twitrends/
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends/trend_modules

cp Twitrends/README.md $RPM_BUILD_ROOT/usr/local/bin/Twitrends
cp -r Twitrends/license $RPM_BUILD_ROOT/usr/local/bin/Twitrends
cp Twitrends/twitrends/trend_modules/__init__.py $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends/trend_modules
cp Twitrends/twitrends/trends_settings.json  $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends
cp Twitrends/twitrends/twitrends.py  $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends
cp Twitrends/twitrends/twitter_ids.txt  $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends
cp Twitrends/twitrends/trend_modules/trend_bot.py  $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends/trend_modules
cp Twitrends/twitrends/trend_modules/settings.py  $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends/trend_modules
cp log/twitrends.log $RPM_BUILD_ROOT/usr/local/log
touch $RPM_BUILD_ROOT/lib/systemd/system/twitrends.service
echo > $RPM_BUILD_ROOT/usr/local/log/twitrends.log # Empty logfile
echo > $RPM_BUILD_ROOT/usr/local/bin/Twitrends/twitrends/twitter_ids.txt # Empty cached ids
exit

%files
%dir %attr(0766, root, root) /usr/local/bin/Twitrends 
%dir %attr(0766, root, root) /usr/local/bin/Twitrends/license
%dir %attr(0766, root, root) /usr/local/bin/Twitrends/twitrends
%dir %attr(0766, root, root) /usr/local/log
%attr(0766, root, root) /usr/local/log/twitrends.log
%attr(0666, root, root) /usr/local/bin/Twitrends/license/LICENSE
%attr(0666, root, root) /usr/local/bin/Twitrends/README.md
%attr(0766, root, root) /usr/local/bin/Twitrends/twitrends/trend_modules/__init__.py
%attr(0666, root, root) /usr/local/bin/Twitrends/twitrends/trends_settings.json
%attr(0766, root, root) /usr/local/bin/Twitrends/twitrends/twitter_ids.txt
%attr(0766, root, root) /usr/local/bin/Twitrends/twitrends/twitrends.py
%attr(0766, root, root) /usr/local/bin/Twitrends/twitrends/trend_modules/settings.py
%attr(0766, root, root) /usr/local/bin/Twitrends/twitrends/trend_modules/trend_bot.py
%attr(0744, root, root) /lib/systemd/system/twitrends.service
# The service should be 0744
# Removed user from service

%install
echo "[Unit]
Description=Twitrends service
After=network.target

[Service]
Type=simple
Restart=on-failure
ExecStart=python3 /usr/local/bin/Twitrends/twitrends/twitrends.py
RestartSec=20

[Install]
WantedBy=multi-user.target" >> $RPM_BUILD_ROOT/lib/systemd/system/twitrends.service


# Add service to systemd
%post
%systemd_post twitrends.service

# Disables and removes twitter_trends.service
%postun
rm /lib/systemd/system/twitrends.service
rm -r /usr/local/bin/Twitrends
rm /usr/local/log/twitrends.log

# Remove service from systemd
%systemd_postun twitrends.service

%changelog
* Sun Aug 29 2021 Peter Yliniemi <peter.yliniemi@gmail.com>
  - Created first RPM package for Twitrends


class Plugin_OBJ():

    def __init__(self, plugin_utils):
        self.plugin_utils = plugin_utils

        self.channels_json_url = "https://iptv-org.github.io/api/channels.json"
        self.streams_json_url = "https://iptv-org.github.io/api/streams.json"

        self.filter_dict = {}
        self.setup_filters()

        self.unfiltered_chan_json = None
        self.filtered_chan_json = None
        self._streams_dict = None

    @property
    def filtered_chan_list(self):
        if not self.filtered_chan_json:
            self.filtered_chan_json = self.filterlist()
        return self.filtered_chan_json

    @property
    def unfiltered_chan_list(self):
        if not self.unfiltered_chan_json:
            self.unfiltered_chan_json = self.get_unfiltered_chan_json()
        return self.unfiltered_chan_json
    
    @property
    def streams_dict(self):
        streams_json = None
        if not self._streams_dict:
            streams_json = self.get_streams_json()
            
        if streams_json:
            self._streams_dict = {}
            for stream in streams_json:
                if stream["channel"]:
                    self._streams_dict[stream["channel"]] = stream
     
        return self._streams_dict

    def setup_filters(self):

        for x in ["country", "languages", "category"]:
            self.filter_dict[x] = []

        for filter in list(self.filter_dict.keys()):

            filterconf = self.plugin_utils.config.dict["iptvorg"]["filter_%s" % filter]
            if filterconf:
                if isinstance(filterconf, str):
                    filterconf = [filterconf]
                self.plugin_utils.logger.info("Found %s Enabled %s Filters" % (len(filterconf), filter))
                self.filter_dict[filter].extend(filterconf)
            else:
                self.plugin_utils.logger.info("Found No Enabled %s Filters" % (filter))

    def get_channels(self):

        channel_list = []

        self.plugin_utils.logger.info("Pulling Unfiltered Channels: %s" % self.channels_json_url)
        self.unfiltered_chan_json = self.get_unfiltered_chan_json()
        self.plugin_utils.logger.info("Found %s Total Channels" % len(self.unfiltered_chan_json))
        self.plugin_utils.logger.info("Found %s Total Streams" % len(self.streams_dict))

        self.filtered_chan_json = self.filterlist()
        self.plugin_utils.logger.info("Found %s Channels after applying filters and Deduping." % len(self.filtered_chan_list))

        for channel_dict in self.filtered_chan_list:
            clean_station_item = {
                                 "name": channel_dict["name"],
                                 "id": channel_dict["id"],
                                 "thumbnail": channel_dict["logo"],
                                 }
            channel_list.append(clean_station_item)

        return channel_list

    def get_channel_stream(self, chandict, stream_args):
        return {"url": self.streams_dict["origin_id"]["url"]}

    def get_unfiltered_chan_json(self):
        urlopn = self.plugin_utils.web.session.get(self.channels_json_url)
        return urlopn.json()
    
    def get_streams_json(self):
        urlopn = self.plugin_utils.web.session.get(self.streams_json_url)
        return urlopn.json()

    def filterlist(self):

        filtered_chan_list = {}
        for channels_item in self.unfiltered_chan_list:
            filters_passed = []
            
            if not self.streams_dict.get(channels_item['id']):
                # Check if there is a stream available for the channel.
                filters_passed.append(False)
            else:                
                for filter_key in list(self.filter_dict.keys()):

                    if not len(self.filter_dict[filter_key]):
                        filters_passed.append(True)
                    else:
                        if filter_key in list(channels_item.keys()):
                            if filter_key in ["country", "languages"]:
                                if isinstance(channels_item[filter_key], list):
                                    if len(channels_item[filter_key]):
                                        chan_values = []
                                        chan_values.extend(channels_item[filter_key])
                                    else:
                                        chan_values = []
                                else:
                                    chan_values = []
                                    chan_values.append(channels_item[filter_key])
                            elif filter_key in ["category"]:
                                chan_values = [channels_item[filter_key]]
                        else:
                            chan_values = []

                        if not len(chan_values):
                            filter_passed = False
                        else:
                            values_passed = []
                            for chan_value in chan_values:
                                if str(chan_value).lower() in [x.lower() for x in self.filter_dict[filter_key]]:
                                    values_passed.append(True)
                                else:
                                    values_passed.append(False)
                            if True in values_passed:
                                filter_passed = True
                            else:
                                filter_passed = False

                        filters_passed.append(filter_passed)

            if False not in filters_passed:
                if not filtered_chan_list.get(channels_item["id"]):
                    self.plugin_utils.logger.debug("Channel '%s' matches the filter." % channels_item["id"])
                    filtered_chan_list[channels_item["id"]] = channels_item

        return filtered_chan_list.values()

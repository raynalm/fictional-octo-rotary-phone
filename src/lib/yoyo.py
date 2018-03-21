def launch_yoyo(node):
    # preprocessing phase
    self.__edges = dict()
        for neighbor in node.neighbors_ids:
            if self.my_id > neighbor:
                self.__edges[neighbor] = IN
            else:
                self.__edges[neighbor] = OUT
        # 3 cases : node can be a source, an intermediate or a sink
        if all([self.__edges[v] == OUT for v in self.__edges]) : # node is a source
            # send id to all
            for v in self.__neighbors_ids:
                self.channel.basic_publish(
                    exchange = '',
                    routing_key = self.__queues[v],
                    body = json.dumps(self.my_id)
                )

        elif all([self.__edges[v] == IN for v in self.__edges]): # node is a sink
            # receive id from all
            for v in neighbors(self):
                channel.basic_consume(
                    self.yo_callback,
                    queue = queue(self, v),
                    no_ack = True
                )

        else:
            # receive id from all in, then send smallest to all out

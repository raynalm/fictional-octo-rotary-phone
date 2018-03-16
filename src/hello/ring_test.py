#!/usr/bin/env python
import pika
import threading


RING_SIZE = 3


def callback(ch, method, properties, body):
    print("received %s" % body)
    ch.stop_consuming()
    print("stopped")


def thread_run(thread_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    queue_send = 'queue'+str(thread_id)
    queue_recv = 'queue'+str((thread_id-1)%RING_SIZE)
    channel.queue_declare(queue=queue_send)
    channel.queue_declare(queue=queue_recv)
    if thread_id == 0:
        channel.basic_publish(exchange='',
                              routing_key=queue_send,
                              body="message trop bien %s" % thread_id)
        print("[%s] finished sending to %s" % (thread_id, queue_send))
        print("[%s] before consume from %s" % (thread_id, queue_recv))
        channel.basic_consume(callback, queue=queue_recv, no_ack=True)
        channel.start_consuming()
        print("[%s] finished consuming" % thread_id)
    else:
        print("[%s] before consume from %s" % (thread_id, queue_recv))
        channel.basic_consume(callback, queue=queue_recv, no_ack=True)
        channel.start_consuming()
        print("[%s] finished consuming" % thread_id)
        channel.basic_publish(exchange='',
                              routing_key=queue_send,
                              body = "message trop bien %s" % thread_id)
        print("[%s] finished sending" % thread_id)


threads = []
for i in range(RING_SIZE):
    t = threading.Thread(target = thread_run, args =(i, ))
    threads += [t]
    t.start()

for t in threads:
    t.join()

print("Main thread exit")

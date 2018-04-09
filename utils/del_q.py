import sys
import pika
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

queues = sys.stdin.readlines()[1:-1]
for x in queues:
    q = x.split()[0]
    print 'Deleting %s...' %(q)
    channel.queue_delete(queue=q)

connection.close()

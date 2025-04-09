from faststream.nats import (
    DiscardPolicy,
    JStream,
    RetentionPolicy,
    StorageType,
)

email_stream = JStream(
    name="email-stream",
    subjects=["email.>"],
    storage=StorageType.FILE,
    retention=RetentionPolicy.WORK_QUEUE,
    max_msgs=100,
    max_msg_size=10 * 1024 * 1024,
    duplicate_window=5 * 60,
)

dead_letters_stream = JStream(
    name="dead-letters-stream",
    subjects=["dead.>"],
    storage=StorageType.FILE,
    retention=RetentionPolicy.LIMITS,
    max_msgs=1000,
    max_msg_size=10 * 1024 * 1024,
    duplicate_window=5 * 60,
    discard=DiscardPolicy.OLD,
)

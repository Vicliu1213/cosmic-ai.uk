import io.aeron.Aeron;
import io.aeron.Subscription;
import io.aeron.driver.MediaDriver;
import java.util.concurrent.atomic.AtomicLong;

public class MarketDataSubscriber {
    private static final AtomicLong received = new AtomicLong();
    private static long lastPrint = System.currentTimeMillis();

    public static void main(String[] args) {
        MediaDriver driver = MediaDriver.launchEmbedded();
        Aeron aeron = Aeron.connect();
        String channel = "aeron:udp?endpoint=224.0.1.1:40456|interface=0.0.0.0";
        Subscription sub = aeron.addSubscription(channel, 1001);
        while (true) {
            sub.poll((buffer, offset, length, header) -> {
                received.incrementAndGet();
                return 1;
            }, 1000);
            if (System.currentTimeMillis() - lastPrint > 2000) {
                long rate = received.getAndSet(0) / 2;
                System.out.println("接收速率: " + rate + " msg/s");
                lastPrint = System.currentTimeMillis();
            }
        }
    }
}

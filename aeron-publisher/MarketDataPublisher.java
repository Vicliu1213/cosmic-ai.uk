import io.aeron.Aeron;
import io.aeron.Publication;
import io.aeron.driver.MediaDriver;
import org.agrona.concurrent.UnsafeBuffer;
import java.nio.ByteBuffer;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;

public class MarketDataPublisher {
    private static final AtomicLong published = new AtomicLong();
    private static long lastPrint = System.currentTimeMillis();

    public static void main(String[] args) throws InterruptedException {
        MediaDriver driver = MediaDriver.launchEmbedded();
        Aeron aeron = Aeron.connect();
        String channel = "aeron:udp?endpoint=224.0.1.1:40456|interface=0.0.0.0";
        Publication pub = aeron.addPublication(channel, 1001);
        UnsafeBuffer buffer = new UnsafeBuffer(ByteBuffer.allocate(256));
        String[] symbols = {"AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"};

        while (true) {
            for (String sym : symbols) {
                double price = 100 + ThreadLocalRandom.current().nextDouble(50);
                int volume = ThreadLocalRandom.current().nextInt(100, 10000);
                String msg = String.format("%s,%.2f,%d", sym, price, volume);
                buffer.putStringAscii(0, msg);
                long result = pub.offer(buffer, 0, msg.length());
                if (result > 0) published.incrementAndGet();
            }
            if (System.currentTimeMillis() - lastPrint > 2000) {
                long rate = published.getAndSet(0) / 2;
                System.out.println("发布速率: " + rate + " msg/s");
                lastPrint = System.currentTimeMillis();
            }
            Thread.sleep(1); // 1ms 节流，可调
        }
    }
}

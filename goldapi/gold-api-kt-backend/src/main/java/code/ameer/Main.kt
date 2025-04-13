package code.ameer

import code.ameer.implementations.TGJUGoldPrice
import redis.clients.jedis.JedisPool
import java.time.Instant
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit


fun main() {

    val pool = JedisPool("redis", 6379)
    val service: PriceService = TGJUGoldPrice()
    val scheduler: ScheduledExecutorService = Executors.newSingleThreadScheduledExecutor()
    val interval = 200L // Interval in seconds
    


    val task = object : Runnable {
        override fun run() {
            try {
                println("Running task at: " + System.currentTimeMillis())
                val price = service.getPrice();
                pool.resource.use { jedis ->
                    jedis.set("gold-price", price.price.toString())
                    jedis.set("gold-price-timestamp", price.timestamp.toString())
                }
                println("Redis set success")
                println("Price: ${price.price}")
                println("Date: ${Instant.ofEpochMilli(price.timestamp).atOffset(ZoneOffset.ofHoursMinutes(3, 30)).format(
                    DateTimeFormatter.ISO_DATE_TIME)}")
            } catch (e: Exception) {
                println("Task failed with exception: ${e.message}")
                e.printStackTrace()
            } finally {
                scheduler.schedule(this, interval, TimeUnit.SECONDS)
            }
        }
    }

    scheduler.schedule(task, 0, TimeUnit.SECONDS)

    Runtime.getRuntime().addShutdownHook(Thread {
        println("Shutting down scheduler...")
        scheduler.shutdown()
    })
}
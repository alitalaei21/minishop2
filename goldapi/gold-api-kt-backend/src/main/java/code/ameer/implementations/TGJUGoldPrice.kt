package code.ameer.implementations

import code.ameer.GoldPrice
import code.ameer.PriceService
import org.jsoup.Jsoup

class TGJUGoldPrice : PriceService() {
    override fun getPrice(): GoldPrice {
        val doc = Jsoup.connect("https://www.tgju.org/profile/geram18").get()
        val el = doc.getElementsByAttributeValue("data-col", "info.last_trade.PDrCotVal").first()!!.text().replace(",", "").toLong().div(10)
        return GoldPrice(el, System.currentTimeMillis())
    }

}
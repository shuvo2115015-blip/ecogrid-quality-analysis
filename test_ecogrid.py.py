import unittest
from ecogrid import MarketplaceService, SettlementService, SmartMeterService


class TestMarketplaceService(unittest.TestCase):

    def setUp(self):
        self.marketplace = MarketplaceService()

    def test_create_trade_success(self):
        trade = self.marketplace.create_trade("buyer1", "seller1", 10, 100)
        self.assertEqual(trade["status"], "Pending")
        self.assertEqual(trade["energy_amount"], 10)

    def test_create_trade_invalid_energy(self):
        with self.assertRaises(ValueError):
            self.marketplace.create_trade("buyer1", "seller1", -5, 100)

    def test_create_trade_invalid_price(self):
        with self.assertRaises(ValueError):
            self.marketplace.create_trade("buyer1", "seller1", 10, 0)

    def test_confirm_trade(self):
        trade = self.marketplace.create_trade("buyer1", "seller1", 10, 100)
        confirmed = self.marketplace.confirm_trade(trade["id"])
        self.assertEqual(confirmed["status"], "Confirmed")

    def test_cancel_trade(self):
        trade = self.marketplace.create_trade("buyer1", "seller1", 10, 100)
        cancelled = self.marketplace.cancel_trade(trade["id"])
        self.assertEqual(cancelled["status"], "Cancelled")

    def test_confirm_nonexistent_trade(self):
        with self.assertRaises(ValueError):
            self.marketplace.confirm_trade(999)


class TestSettlementService(unittest.TestCase):

    def setUp(self):
        self.settlement = SettlementService()
        self.settlement.create_wallet("user1", 500)

    def test_reserve_funds_success(self):
        result = self.settlement.reserve_funds("user1", 100)
        self.assertTrue(result)

    def test_reserve_funds_insufficient(self):
        with self.assertRaises(ValueError):
            self.settlement.reserve_funds("user1", 1000)

    def test_release_funds(self):
        self.settlement.reserve_funds("user1", 100)
        result = self.settlement.release_funds("user1", 100)
        self.assertTrue(result)

    def test_wallet_not_found(self):
        with self.assertRaises(ValueError):
            self.settlement.reserve_funds("unknown_user", 100)

    def test_duplicate_wallet(self):
        with self.assertRaises(ValueError):
            self.settlement.create_wallet("user1", 100)


class TestSmartMeterService(unittest.TestCase):

    def setUp(self):
        self.meter = SmartMeterService()
        self.meter.register_meter("meter_001", "Melbourne")

    def test_register_meter_success(self):
        meter = self.meter.register_meter("meter_002", "Sydney")
        self.assertEqual(meter["status"], "Active")

    def test_duplicate_meter_registration(self):
        with self.assertRaises(ValueError):
            self.meter.register_meter("meter_001", "Melbourne")

    def test_record_reading_success(self):
        reading = self.meter.record_reading("meter_001", 50, 20)
        self.assertEqual(reading["net_energy"], 30)

    def test_record_negative_energy(self):
        with self.assertRaises(ValueError):
            self.meter.record_reading("meter_001", -10, 20)

    def test_allocate_energy_success(self):
        self.meter.record_reading("meter_001", 50, 20)
        result = self.meter.allocate_energy("meter_001", 25)
        self.assertTrue(result)

    def test_allocate_energy_insufficient(self):
        self.meter.record_reading("meter_001", 10, 8)
        with self.assertRaisesRegex(Exception, "Energy Allocation Failed"):
            self.meter.allocate_energy("meter_001", 100)


if __name__ == "__main__":
    unittest.main()
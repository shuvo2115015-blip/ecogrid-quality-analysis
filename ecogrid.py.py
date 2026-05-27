class MarketplaceService:
    """Manages peer-to-peer energy trading between market participants."""

    def __init__(self):
        self.trades = []
        self.offers = []

    def create_trade(self, buyer_id, seller_id, energy_amount, price):
        if energy_amount <= 0:
            raise ValueError("Energy amount must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")

        trade = {
            "id": len(self.trades) + 1,
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "energy_amount": energy_amount,
            "price": price,
            "status": "Pending"
        }
        self.trades.append(trade)
        print(f"Trade Status: Pending - Trade ID: {trade['id']}")
        return trade

    def confirm_trade(self, trade_id):
        for trade in self.trades:
            if trade["id"] == trade_id:
                trade["status"] = "Confirmed"
                print(f"Trade Status: Confirmed - Trade ID: {trade_id}")
                return trade
        raise ValueError(f"Trade {trade_id} not found")

    def cancel_trade(self, trade_id):
        for trade in self.trades:
            if trade["id"] == trade_id:
                trade["status"] = "Cancelled"
                print(f"Trade Status: Cancelled - Trade ID: {trade_id}")
                return trade
        raise ValueError(f"Trade {trade_id} not found")

    def get_active_trades(self):
        return [t for t in self.trades if t["status"] == "Pending"]


class SettlementService:
    """Manages ledger accounts, funding reserves, and payment processing."""

    def __init__(self):
        self.wallets = {}
        self.transactions = []

    def create_wallet(self, user_id, initial_balance=0):
        if user_id in self.wallets:
            raise ValueError(f"Wallet already exists for user {user_id}")
        self.wallets[user_id] = initial_balance
        return self.wallets[user_id]

    def reserve_funds(self, user_id, amount):
        if user_id not in self.wallets:
            raise ValueError(f"Wallet not found for user {user_id}")
        if self.wallets[user_id] < amount:
            raise ValueError("Insufficient funds")
        self.wallets[user_id] -= amount
        print("Funds Reserved")
        return True

    def release_funds(self, user_id, amount):
        if user_id not in self.wallets:
            raise ValueError(f"Wallet not found for user {user_id}")
        self.wallets[user_id] += amount
        print("Funds Released")
        return True

    def process_payment(self, sender_id, receiver_id, amount):
        self.reserve_funds(sender_id, amount)
        self.wallets[receiver_id] = self.wallets.get(receiver_id, 0) + amount
        
        transaction = {
            "id": len(self.transactions) + 1,
            "sender": sender_id,
            "receiver": receiver_id,
            "amount": amount,
            "status": "Completed"
        }
        self.transactions.append(transaction)
        return transaction


class SmartMeterService:
    """Ingests data from IoT infrastructure and tracks grid allocation capabilities."""

    def __init__(self):
        self.meters = {}
        self.readings = []

    def register_meter(self, meter_id, location):
        if meter_id in self.meters:
            raise ValueError(f"Meter {meter_id} already registered")
        self.meters[meter_id] = {
            "location": location,
            "status": "Active"
        }
        return self.meters[meter_id]

    def record_reading(self, meter_id, energy_generated, energy_consumed):
        if meter_id not in self.meters:
            raise ValueError(f"Meter {meter_id} not found")
        if energy_generated < 0 or energy_consumed < 0:
            raise ValueError("Energy values cannot be negative")

        reading = {
            "meter_id": meter_id,
            "energy_generated": energy_generated,
            "energy_consumed": energy_consumed,
            "net_energy": energy_generated - energy_consumed
        }
        self.readings.append(reading)
        return reading

    def allocate_energy(self, meter_id, amount):
        energy_available = False

        for reading in self.readings:
            if reading["meter_id"] == meter_id:
                if reading["net_energy"] >= amount:
                    energy_available = True
                    break

        if energy_available:
            print("Energy Allocated")
            return True
        else:
            raise Exception("Energy Allocation Failed")

    def get_meter_status(self, meter_id):
        if meter_id not in self.meters:
            raise ValueError(f"Meter {meter_id} not found")
        return self.meters[meter_id]


class EcoGridSystem:
    """Orchestrates system modules using a Saga transaction pattern."""

    def __init__(self):
        self.marketplace = MarketplaceService()
        self.settlement = SettlementService()
        self.meter = SmartMeterService()

    def execute_energy_trade(self, buyer_id, seller_id, meter_id, energy_amount, price):
        trade = None
        try:
            trade = self.marketplace.create_trade(buyer_id, seller_id, energy_amount, price)
            self.settlement.reserve_funds(buyer_id, price)
            self.meter.allocate_energy(meter_id, energy_amount)
            self.marketplace.confirm_trade(trade["id"])

            print("Trade completed successfully")
            return trade

        except Exception as e:
            print("Compensation Transaction Started")
            self.settlement.release_funds(buyer_id, price)
            
            # Safe boundary check: Only try to cancel if the trade object was actually created
            if trade and "id" in trade:
                self.marketplace.cancel_trade(trade["id"])
                
            print(f"Trade failed: {e}")
            return None


if __name__ == "__main__":
    system = EcoGridSystem()

    system.settlement.create_wallet("buyer_1", 1000)
    system.settlement.create_wallet("seller_1", 500)
    system.meter.register_meter("meter_001", "Melbourne")
    system.meter.record_reading("meter_001", 50, 20)

    result = system.execute_energy_trade("buyer_1", "seller_1", "meter_001", 25, 100)
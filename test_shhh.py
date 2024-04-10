import unittest

from shhh import ShhBot

class TestShhh(unittest.TestCase):
    def test_checkUser(self):
        shhBot = ShhBot()
        self.assertTrue(shhBot.checkUser("1234567890", None)) 
        self.assertTrue(shhBot.checkUser("1234567890", "1234567890")) 
        self.assertFalse(shhBot.checkUser("1234567890", "1234567891")) 
        self.assertTrue(shhBot.checkUser("1234567890", "1234567890 1234567891")) 
        self.assertFalse(shhBot.checkUser("1234567890", "1234567892 1234567891"))
    
    def test_checkUserEnv(self):
        shhBot = ShhBot()
        shhBot.ALLOWED_CHAT_IDS="1234567890 1234567891" 
        testChatId = "1234567890"
        self.assertTrue(shhBot.checkUser(testChatId, shhBot.ALLOWED_CHAT_IDS)) 
        testChatId = "1234567822"
        self.assertFalse(shhBot.checkUser(testChatId, shhBot.ALLOWED_CHAT_IDS)) 

if __name__ == '__main__':
    unittest.main()

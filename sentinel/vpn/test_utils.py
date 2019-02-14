from utils import convert_to_seconds, convert_bandwidth
import unittest



class TestApiUnit(unittest.TestCase):
    
    def test_convert_to_seconds(self):
        tests = [
            ('1 minute,34 seconds',94),
            ('1 minute,1 second',61),
            ('now',0),
            ('55 seconds', 55),
            ('10 minutes, 59 seconds',659),
            ('', 0),
            ('1 minute',60)
            ]
        for value, expected in tests:
            with self.subTest(value=value):
                self.assertEqual(convert_to_seconds(value), expected)

    def test_convert_bandwidth(self):
        tests = [
            ('2.68 MiB received, 400.80 KiB sent',{'download':410419.2, 'upload': 2810183.68 }),
            ('1 MiB received, 1 KiB sent',{'download': 1024.0, 'upload': 1048576.0 }),
            ('2 MiB received, 22.22 MiB sent',{'download': 23299358.72, 'upload': 2097152.0 })
        ]
        for value, expected in tests:
            with self.subTest(value=value):
                self.assertEqual(convert_bandwidth(value), expected)


if __name__ == '__main__':
    unittest.main()

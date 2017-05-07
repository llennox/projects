


#build functional tests that has user upload photo without EXIF data,  fail, upload new photo with EXIF data matching location, navigate to 
#photo viewing view, find uploaded photo, comment on photo, upload new photo, downvote/upvote confirm position of photos is correct. 
from selenium import webdriver
import unittest

class NewVisitorTest(unittest.TestCase):  

    def setUp(self):  
        self.browser = webdriver.Firefox()

    def tearDown(self):  
        self.browser.quit()

    def test_can_upload_photo(self):  
        
        self.browser.get('http://localhost:8000')


        self.assertIn('home', self.browser.title)  
        


    def test_can_upload_photo(self):  
        
        self.browser.get('http://localhost:8000/upload')


        self.assertIn('Upload', self.browser.title)  
        self.fail('Finish the test!')  

      

if __name__ == '__main__':  
    unittest.main()  

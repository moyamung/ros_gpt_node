#!/usr/bin/env python3.7
import roslib
import rospy
import rospkg

from std_msgs.msg import String
from sensor_msgs.msg import Image
from final_result_msgs.msg import save_image
from cv_bridge import CvBridge, CvBridgeError

import openai

class GPT():
    def __init__(self):
        #ROS init
        rospy.init_node('gpt_node')
        self.rate = rospy.Rate(100.0)
        
        self.publisher = rospy.Publisher('/target_detection', save_image, queue_size=5)
        self.img_subscriber = rospy.Subscriber('/camera/color/image_raw', Image, self.image_saver)
        self.qr_subscriber = rospy.Subscriber('/qr_codes', String, self.solve_riddle)
        
        # self.key2 = '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'
        # self.key = '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' 
        self.key = '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'
        # self.org = 'org-YO1ZYFQNmHZeXB9zdcGdd8TH'
        #self.client = OpenAI(api_key=self.key)
        openai.api_key = self.key
        
        self.solved_riddles = set()
        
        self.model = 'text-davinci-003'

        #self.model = 'davinci'
        
        self.last_image_msg = None
        
    def image_saver(self, msg):
        self.last_image_msg = msg
        
    def solve_riddle(self, msg):
        riddle = msg.data
        
        if (riddle in self.solved_riddles):
            print("duplicated answer")
            return
        
        
        message = [
            {
                "role": "user",

                "content": riddle
            }
        ]
        
        response = openai.completions.create(
            model=self.model,
            prompt = "Answer only in numbers:" + riddle
        )
        
        #print(response)


        print(response.choices[0].text.strip())
        
        try:
            id = int(response.choices[0].text.strip())
            
            pub_msg = save_image()
            
            pub_msg.class_id = id
            pub_msg.save_img = self.last_image_msg
            pub_msg.x_pose = 0
            pub_msg.y_pose = 0
            
            self.publisher.publish(pub_msg)
            
            self.solved_riddles.add(riddle)
        except:
            print("solved wrong")

def main():
    #rospack = rospkg.RosPack()
    
    gpt = GPT()
    
    while not rospy.is_shutdown():
        gpt.rate.sleep()
        
if __name__ == '__main__':
    main()
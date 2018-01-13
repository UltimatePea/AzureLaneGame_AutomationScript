
# coding: utf-8

# In[6]:


import wda
import cv2
import time


# In[7]:


c = wda.Client('http://192.168.86.33:8100')
print(c.status())
s = c.session()


# In[8]:


_ = c.screenshot('screen.png')


# In[9]:


# get some global properties
globalScreen = cv2.imread("screen.png",0)
screenWidth, screenHeight = globalScreen.shape[::-1]
print("ScreenWidth: {0}, ScreenHeight: {1}".format(screenWidth, screenHeight))


# In[10]:


def getSimilarity(template, img):
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img,template,cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print("Max Value is {0}".format(max_val))
    return max_val


# In[11]:


def takeScreenShot():
    c.screenshot('temp.png')
    img = cv2.imread('temp.png', 0)
    return img


# In[12]:


# get the location of template on image
def getButtonLocation(template, img): 
    #c.screenshot('temp.png')
    #template = cv2.imread(buttonImageName,0)
    #img = cv2.imread('temp.png', 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    touch_loc = (max_loc[0] + w/2, max_loc[1] + h/2)
    return (touch_loc, max_loc, w, h)


# In[13]:


# touch the template on the image with offsets
def touchButton(template, img, xoffset=0, yoffset=0): 
    touch_loc, _, _, _ = getButtonLocation(template, img)
    t_x, t_y = (touch_loc[0]+xoffset, touch_loc[1]+yoffset)
    print("Touching {0}, {1}".format(t_x, t_y))
    s.tap(t_x, t_y)


# In[14]:


def recognizeAndProcessPage(specs): # in the form of imageName => (template, action)
    img = takeScreenShot()
    print("===========================")
    # pick the highest applicable key
    ss = max(specs, key=lambda s : getSimilarity(s.imageTemplate, img))
    # perform second filtering to filter by the actionButtonTemplate
    filtered = [s for s in specs if s.imageName == ss.imageName]
    print("= = = = = = = = = = = = = =")

    ss = max(filtered, key=lambda s : getSimilarity(s.actionTemplate,img))
    print("Picked : " + ss.imageName + " ==> " + ss.actionButtonName)
    ss.action(ss.actionTemplate, img)
    


# In[15]:


class Spec:
    # imageName : the image to scan to identify the scene
    # action : the action to execute upon match with imageName, receives (template, img), where
    #           template is the cv2 rep of the actionButtonName below, and the image is the 
    #           current screen shot
    # actionButtonName: sometimes we want different button to be clicked while not checking this button
    #           the default value is the same as imageName
    def __init__(self, imageName, action, actionButtonName = None):
        if actionButtonName is None:
            actionButtonName = imageName
        self.imageName = imageName;
        self.action = action # action must receive (template, img) as the input variable
        self.actionButtonName = actionButtonName
        
        # load resources
        self.imageTemplate = cv2.imread(imageName, 0)
        self.actionTemplate = cv2.imread(actionButtonName, 0)
        print("\nProcessing Spec: \nImageName: {0}\nActionButtonName : {1}".format(
            imageName, actionButtonName))
        template1 = cv2.imread(imageName, 0)
        if self.imageTemplate is None:
            print("Error : ImageName is wrong")
        template2 = cv2.imread(actionButtonName, 0)
        if self.actionTemplate is None:
            print("Error : ActionButtonName is wrong")


# In[16]:


def loginScreenSpec():
    def f(template, img):
        touchButton(template, img, 200)
    return Spec("LoginServerSelection.png", f)


# In[17]:


def closeEventScreenSpec():
    def f(template, img):
        touchButton(template, img, 0, -270)
    return Spec("EventOverview.png", f)


# In[18]:


def closeAnnouncementScreenSpec():
    return Spec("SystemAnnouncement.png", touchButton, "CrossCloseButton.png")


# In[19]:


def startBattleFromHomeScreenSpec():
    return Spec("StartBattleHomeScreen.png", touchButton)


# In[20]:


def ChooseBattleLevelSpec():
    return Spec("MapLevelSelectionClear.png", touchButton)


# In[21]:


def ChooseBattleLevelConfirmSpec():
    return Spec("ChooseLevelGoNowButton.png", touchButton)


# In[22]:


def MapMoveSpecOneBullet():
    def f(template, img):
        touchButton(template, img, -30, 30)
    return Spec("ExploreMapDetectionImage.png", f, "OneBulletButton.png")


# In[23]:


def MapMoveSpecTwoBullet():
    def f(template, img):
        touchButton(template, img, -30, 30)
    return Spec("ExploreMapDetectionImage.png", f, "TwoBulletButton.png")


# In[24]:


def MapMoveSpecQuestionMark():
    def f(template, img):
        touchButton(template, img, -130)
    return Spec("ExploreMapDetectionImage.png", f, "ExploreMapQuestionMark.png")


# In[25]:


def MapMoveSpecBoss():
    return Spec("ExploreMapDetectionImage.png", touchButton, "BossIconDetection.png")


# In[26]:


def MapMoveSpecShip1():
    return Spec("ExploreMapDetectionImage.png", touchButton, "MapShipType1.png")


# In[27]:


def MapMoveSpecShip2():
    return Spec("ExploreMapDetectionImage.png", touchButton, "MapShipType2.png")


# In[28]:


def MapMoveSpecShip3():
    return Spec("ExploreMapDetectionImage.png", touchButton, "MapShipType3.png")


# In[29]:


def MapMoveAmbushEncountered():
    return Spec("AmbushEncounteredDetection.png", touchButton, "MapMoveFightAmbush.png")


# In[30]:


def MapBattlePreviewSpec():
    return Spec("BattlePreviewStartButton.png", touchButton)


# In[31]:


def BattleStartAutoFightSpec():
    return Spec("NotAutoFightingDetection.png", touchButton)


# In[32]:


def BattleStartAutoFightConfirmationSpec():
    return Spec("StartAutoBattleWarningDetection.png", touchButton, "StartAutoBattleWarningConfirmationButton.png")


# In[33]:


def BattleInGoodState():
    def f(template, img):
        pass
    return Spec("StopAutoBattleDetection.png", f)


# In[34]:


def BattlePostViewContinueLevelSSpec():
    return Spec("BattlePostViewSLevel.png", touchButton)


# In[35]:


def BattlePostViewGetItems():
    return Spec("BattlePostViewGetItemsDetection.png", touchButton)


# In[36]:


def BattlePostViewConfirmToContinue():
    return Spec("BattlePostViewGetItemsDetection.png", touchButton, "PostBattleConfirmButton.png")


# In[37]:


def BattlePostViewNewCharacterConfirmation():
    def f(template, img):
        touchButton(template, img, 0, 200)
    return Spec("PostBattleNewCharacterDetection.png", f)


# In[38]:


def BattlePostViewNewCharacterLockinConfirmation():
    return Spec("WhetherLockingThisShipDetection.png", touchButton, "ShipLockinYesButton.png")


# In[39]:


def DismissInfoBoxSpec():
    return Spec("InfoBoxDetection.png", touchButton, "CrossCloseButton.png")


# In[41]:


specs = [loginScreenSpec, closeEventScreenSpec, closeAnnouncementScreenSpec, 
         startBattleFromHomeScreenSpec, ChooseBattleLevelSpec, ChooseBattleLevelConfirmSpec,
        #MapMoveSpecOneBullet, MapMoveSpecTwoBullet, 
         MapMoveSpecQuestionMark,
         MapMoveAmbushEncountered, MapBattlePreviewSpec, BattleStartAutoFightSpec,
         BattleStartAutoFightConfirmationSpec,BattlePostViewNewCharacterConfirmation,
         BattlePostViewNewCharacterLockinConfirmation,MapMoveSpecBoss,
        BattlePostViewContinueLevelSSpec, BattlePostViewGetItems, BattlePostViewConfirmToContinue,
        MapMoveSpecShip1, MapMoveSpecShip2, MapMoveSpecShip3, BattleInGoodState,DismissInfoBoxSpec
        
        ]
specs = [s() for s in specs]
while(True):
    recognizeAndProcessPage(specs)
    time.sleep(1)


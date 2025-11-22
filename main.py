from people_counting import people_counting

if __name__ == "__main__":
    #test1
    area2 = [(280, 665), (300, 620), (150, 485), (105, 505)]
    area1 = [(60, 525), (95, 510), (270, 675), (220, 695)]
    people_counting(area1,area2, register_line_area=[(0,0),(0,0)], show_video=True, VIDEO_PATH='test_1.mp4')

    register_line_area = [(50,270), (360,600)]
    people_counting(None,None, register_line_area=register_line_area, show_video=True,VIDEO_PATH='queue_test_vid.mp4', TIME_PER_CUSTOMER=10)

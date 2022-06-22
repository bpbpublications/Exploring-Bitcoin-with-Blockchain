from ContentHash import contentHash

story = '''Best Friend Lunch Party: One day two best friends, a monkey and a crocodile decided to have lunch together in a farm. The next day they passed the river and reached the farm. After a heavy meal the monkey got up and started growling loudly. The frightened crocodile pleaded the monkey to stop. But the monkey said, 'I have a habit of growling after every meal, I cannot help it'. The monkey was on the crocodiles back while crossing the river back home. When they were halfway through the river, the crocodile took a dip in the water. When the monkey was frightened, the crocodile said, 'I have a habit of taking a dip in the water after every meal, I cannot help it'. Monkey understood his mistake.'''

if __name__ == '__main__':
    content_hs = contentHash(story).hex()
    print(content_hs)

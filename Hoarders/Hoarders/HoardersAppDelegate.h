//
//  HoardersAppDelegate.h
//  Hoarders
//
//  Created by Sidd Sathyam on 6/23/13.
//  Copyright (c) 2013 Sidd Sathyam. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "HoardersConstants.h"
#import "HoardersPythonExtension.h"

@interface HoardersAppDelegate : NSObject <NSApplicationDelegate> {
	NSFileManager* fm;
    NSMutableDictionary* pathModificationDates;
    NSNumber* lastEventId;
    FSEventStreamRef stream;
}

@property (assign) IBOutlet NSWindow *window;
@property (strong, nonatomic) IBOutlet NSMenu *statusMenu;
@property (strong, nonatomic) NSStatusItem *statusItem;

- (void) registerDefaults;
- (void) initializeEventStream;
- (void )updateLastEventId: (uint64_t) eventId;

@end

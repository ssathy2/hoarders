//
//  HoardersAppDelegate.m
//  Hoarders
//
//  Created by Sidd Sathyam on 6/23/13.
//  Copyright (c) 2013 Sidd Sathyam. All rights reserved.
//

#import "HoardersAppDelegate.h"

@implementation HoardersAppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
	// Insert code here to initialize your application
}

-(void)awakeFromNib{
	self.statusItem = [[NSStatusBar systemStatusBar] statusItemWithLength:NSVariableStatusItemLength];
	[self.statusItem setMenu:self.statusMenu];
	[self.statusItem setTitle:@"H"];
	[self.statusItem setHighlightMode:YES];
	[self initializeEventStream];
}

- (void) registerDefaults
{
	
}

- (void) updateLastEventId:(uint64_t)eventId
{
	
}

- (void) initializeEventStream
{
    NSString *myPath = HOARDERS_PATH;
    NSArray *pathsToWatch = [NSArray arrayWithObject:myPath];
    void *appPointer = (__bridge void *)self;
    FSEventStreamContext context = {0, appPointer, NULL, NULL, NULL};
    NSTimeInterval latency = 3.0;
    stream = FSEventStreamCreate(NULL,
                                 &fsevents_callback,
                                 &context,
                                 (__bridge CFArrayRef) pathsToWatch,
								 kFSEventStreamEventIdSinceNow,
                                 (CFAbsoluteTime) latency,
                                 kFSEventStreamCreateFlagUseCFTypes | kFSEventStreamCreateFlagFileEvents
								 );
	
    FSEventStreamScheduleWithRunLoop(stream,
                                     CFRunLoopGetCurrent(),
                                     kCFRunLoopDefaultMode);
    FSEventStreamStart(stream);
}

void print_eventflags(const FSEventStreamEventFlags eventFlag)
{
	printf("Flags: \n");
	if(eventFlag & kFSEventStreamEventFlagNone) printf("kFSEventStreamFlagNone \n");
	if(eventFlag & kFSEventStreamEventFlagMustScanSubDirs) printf("kFSEventStreamEventFlagMustScanSubDirs \n");
	if(eventFlag & kFSEventStreamEventFlagUserDropped) printf("kFSEventStreamEventFlagUserDropped \n");
	if(eventFlag & kFSEventStreamEventFlagItemCreated) printf("kFSEventStreamEventFlagItemCreated \n");
	if(eventFlag & kFSEventStreamEventFlagItemRemoved) printf("kFSEventStreamEventFlagItemRemoved \n");
	if(eventFlag & kFSEventStreamEventFlagItemInodeMetaMod) printf("kFSEventStreamEventFlagItemInodeMetaMod \n");
	if(eventFlag & kFSEventStreamEventFlagItemRenamed) printf("kFSEventStreamEventFlagItemRenamed \n");
	if(eventFlag & kFSEventStreamEventFlagItemIsFile) printf("kFSEventStreamEventFlagItemIsFile \n");
	if(eventFlag & kFSEventStreamEventFlagItemIsDir) printf("kFSEventStreamEventFlagItemIsDir \n");
	
	/*kFSEventStreamEventFlagMustScanSubDirs = 0x00000001,
	kFSEventStreamEventFlagUserDropped = 0x00000002,
	kFSEventStreamEventFlagKernelDropped = 0x00000004,
	kFSEventStreamEventFlagEventIdsWrapped = 0x00000008,
	kFSEventStreamEventFlagHistoryDone = 0x00000010,
	kFSEventStreamEventFlagRootChanged = 0x00000020,
	kFSEventStreamEventFlagMount = 0x00000040,
	kFSEventStreamEventFlagUnmount = 0x00000080,
	kFSEventStreamEventFlagItemCreated = 0x00000100,
	kFSEventStreamEventFlagItemRemoved = 0x00000200,
	kFSEventStreamEventFlagItemInodeMetaMod = 0x00000400,
	kFSEventStreamEventFlagItemRenamed = 0x00000800,
	kFSEventStreamEventFlagItemModified = 0x00001000,
	kFSEventStreamEventFlagItemFinderInfoMod = 0x00002000,
	kFSEventStreamEventFlagItemChangeOwner = 0x00004000,
	kFSEventStreamEventFlagItemXattrMod = 0x00008000,
	kFSEventStreamEventFlagItemIsFile = 0x00010000,
	kFSEventStreamEventFlagItemIsDir = 0x00020000,
	kFSEventStreamEventFlagItemIsSymlink = 0x00040000*/
}

void fsevents_callback(ConstFSEventStreamRef streamRef,
                       void *userData,
                       size_t numEvents,
                       NSArray* eventPaths,
                       const FSEventStreamEventFlags eventFlags[],
                       const FSEventStreamEventId eventIds[])
{
	HoardersAppDelegate* app = (__bridge HoardersAppDelegate*) userData;
	
	NSMutableArray* eventFlagsArr = [[NSMutableArray alloc] init];
	NSMutableArray* eventIdsArr = [[NSMutableArray alloc] init];
	
	for (int i=0; i<numEvents; i++) {
	
        /* flags are unsigned long, IDs are uint64_t */
		printf("Change %llu in %s, flags 0x%x\n", eventIds[i], [eventPaths[i] UTF8String], eventFlags[i]);
		print_eventflags(eventFlags[i]);
		
		[eventFlagsArr addObject: [NSNumber numberWithUnsignedLong: eventFlags[i]]];
		[eventIdsArr addObject: [NSNumber numberWithUnsignedLongLong: eventIds[i]]];
	}
	printf("\n");
	[app handleEventsWithNumEvents: [[NSNumber numberWithUnsignedLongLong: numEvents] longValue] paths: eventPaths eventFlags: eventFlagsArr eventIds: eventIdsArr];
}

- (void) handleEventsWithNumEvents: (long)numEvents paths: (NSArray*)paths eventFlags:(NSArray*)eventFlags eventIds:(NSArray*)eventIds
{
	NSMutableArray* modifiedDirArr = [[NSMutableArray alloc] init];
	NSMutableArray* modifiedFileArr = [[NSMutableArray alloc] init];
	
	NSURL* filePath;
	for(int i=0; i < numEvents; i++){
		filePath = [NSURL fileURLWithPath: paths[i]];
		
		if([[filePath lastPathComponent] rangeOfString: @"." options: NSCaseInsensitiveSearch].location != 0)
		{
			if([self isEventDirCreated: (FSEventStreamEventFlags)[eventFlags[i] unsignedLongValue]] || [self isEventDirModified: (FSEventStreamEventFlags)[eventFlags[i] unsignedLongValue]])
			{
				[modifiedDirArr addObject: filePath];
			}
			if([self isEventFileCreated: (FSEventStreamEventFlags)[eventFlags[i] unsignedLongValue]] || [self isEventFileModified: (FSEventStreamEventFlags)[eventFlags[i] unsignedLongValue]])
			{
				[modifiedFileArr addObject: filePath];
			}
		}
		
	}
	
	if([modifiedDirArr count] > 0) [HoardersPythonExtension runDirChangeScriptWithPaths: modifiedDirArr];
	if([modifiedFileArr count] > 0) [HoardersPythonExtension runDirChangeScriptWithPaths: modifiedFileArr];
}

- (bool) isEventDir: (const FSEventStreamEventFlags) flag
{
	return (flag & kFSEventStreamEventFlagItemIsFile)?YES:NO;
}

- (bool) isEventFile: (const FSEventStreamEventFlags) flag
{
	return (flag & kFSEventStreamEventFlagItemIsDir)?YES:NO;
}

- (bool) isEventDirCreated: (const FSEventStreamEventFlags) flag
{
	return ((flag & kFSEventStreamEventFlagItemIsDir) && (flag & kFSEventStreamEventFlagItemCreated))?YES:NO;
}

- (bool) isEventFileCreated: (const FSEventStreamEventFlags) flag
{
	return ((flag & kFSEventStreamEventFlagItemIsFile) && (flag & kFSEventStreamEventFlagItemCreated))?YES:NO;
}

- (bool) isEventDirModified: (const FSEventStreamEventFlags) flag
{
	return ((flag & kFSEventStreamEventFlagItemIsDir) && (flag & kFSEventStreamEventFlagItemModified))?YES:NO;
}

- (bool) isEventFileModified: (const FSEventStreamEventFlags) flag
{
	return ((flag & kFSEventStreamEventFlagItemIsFile) && (flag & kFSEventStreamEventFlagItemModified))?YES:NO;
}

- (NSApplicationTerminateReply)applicationShouldTerminate: (NSApplication *)app
{
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults setObject:lastEventId forKey:@"lastEventId"];
    [defaults setObject:pathModificationDates forKey:@"pathModificationDates"];
    [defaults synchronize];
    FSEventStreamStop(stream);
    FSEventStreamInvalidate(stream);
    return NSTerminateNow;
}

@end
